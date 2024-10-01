/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState, useSubEnv } from "@odoo/owl";
import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";
import { patch } from "@web/core/utils/patch"

patch(ProductConfiguratorDialog.prototype, {
  
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        
        onWillStart(async() => {
            const { products, optional_products, accessory_products, alternate_products, replacement_product } = await this._loadPartData(this.props.edit);
            this.state.accessoryProducts = accessory_products;
            this.state.alternateProducts = alternate_products;
            this.state.replacementProduct = replacement_product;
        });
    },

    async _loadPartData(onlyMainProduct) {
        return this.rpc('/sale_product_configurator/get_part_values', {
            product_template_id: this.props.productTemplateId,
            quantity: this.props.quantity,
            currency_id: this.props.currencyId,
            so_date: this.props.soDate,
            product_uom_id: this.props.productUOMId,
            company_id: this.props.companyId,
            pricelist_id: this.props.pricelistId,
            ptav_ids: this.props.ptavIds,
            only_main_product: onlyMainProduct,
        });
    },

    async _getAccessoryProducts(product) {
        return this.rpc('/sale_product_configurator/get_accessory_products', {
            product_template_id: product.product_tmpl_id,
            combination: this._getCombination(product),
            parent_combination: this._getParentsCombination(product),
            currency_id: this.props.currencyId,
            so_date: this.props.soDate,
            company_id: this.props.companyId,
            pricelist_id: this.props.pricelistId,
        });
    },

    async _addProduct(productTmplId) {
        const indexOptional = this.state.optionalProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        const indexAccessory = this.state.accessoryProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        if (indexOptional >= 0) {
            this.state.products.push(...this.state.optionalProducts.splice(indexOptional, 1));
            const product = this._findProduct(productTmplId);
            let newOptionalProducts = await this._getOptionalProducts(product);
            for(const newOptionalProductDict of newOptionalProducts) {
                const newProduct = this._findProduct(newOptionalProductDict.product_tmpl_id);
                if (newProduct) {
                    newOptionalProducts = newOptionalProducts.filter(
                        (p) => p.product_tmpl_id != newOptionalProductDict.product_tmpl_id
                    );
                    newProduct.parent_product_tmpl_ids.push(productTmplId);
                }
            }
            if (newOptionalProducts) this.state.optionalProducts.push(...newOptionalProducts);
        }
        if (indexAccessory >= 0) {
            this.state.products.push(...this.state.accessoryProducts.splice(indexAccessory, 1));
            const product = this._findProduct(productTmplId);
            let newAccessoryProducts = await this._getAccessoryProducts(product);
            for(const newAccessoryProductDict of newAccessoryProducts) {
                const newProduct = this._findProduct(newAccessoryProductDict.product_tmpl_id);
                if (newProduct) {
                    newAccessoryProducts = newAccessoryProducts.filter(
                        (p) => p.product_tmpl_id != newAccessoryProductDict.product_tmpl_id
                    );
                    newProduct.parent_product_tmpl_ids.push(productTmplId);
                }
            }
            if (newAccessoryProducts) this.state.accessoryProducts.push(...newAccessoryProducts);
        }
    },

    _removeProduct(productTmplId) {
        const index = this.state.products.findIndex(p => p.product_tmpl_id === productTmplId);
        if (index >= 0) {
            const product = this.state.products.splice(index, 1)[0];
    
            const isOptionalProduct = this.state.optionalProducts.some(p => p.product_tmpl_id === productTmplId);
            if (isOptionalProduct) {
                this.state.optionalProducts.push(product);
            } else {
                this.state.accessoryProducts.push(product);
            }
    
            for (const childProduct of this._getChildProducts(productTmplId)) {
                childProduct.parent_product_tmpl_ids = childProduct.parent_product_tmpl_ids.filter(
                    id => id !== productTmplId
                );
                if (!childProduct.parent_product_tmpl_ids.length) {
                    this._removeProduct(childProduct.product_tmpl_id);
                    this.state.optionalProducts.splice(
                        this.state.optionalProducts.findIndex(
                            p => p.product_tmpl_id === childProduct.product_tmpl_id
                        ), 1
                    );
                    this.state.accessoryProducts.splice(
                        this.state.accessoryProducts.findIndex(
                            p => p.product_tmpl_id === childProduct.product_tmpl_id
                        ), 1
                    );
                }
            }
        }
    },

    _findProduct(productTmplId) {
        return  this.state.products.find(p => p.product_tmpl_id === productTmplId) ||
                this.state.optionalProducts.find(p => p.product_tmpl_id === productTmplId) ||
                this.state.accessoryProducts.find(p => p.product_tmpl_id === productTmplId)
    },

});
