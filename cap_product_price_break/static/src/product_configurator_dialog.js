/** @odoo-module */

import {SaleOrderLineProductField} from '@sale/js/sale_product_field';
import {serializeDateTime} from "@web/core/l10n/dates";
import {x2ManyCommands} from "@web/core/orm_service";
import {WarningDialog} from "@web/core/errors/error_dialogs";

import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import {Component, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {
    ProductConfiguratorDialog
} from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";
import {patch} from "@web/core/utils/patch";


patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.title = "";
        onWillStart(async () => {
            const {
                products,
                optional_products,
                accessory_products,
                alternate_products,
            } = await this._loadPartData(this.props.edit);
            this.state.products = products || [];
            this.state.optionalProducts = optional_products || [];
            this.state.accessoryProducts = accessory_products || [];
            this.state.alternateProducts = alternate_products || [];
        });
    },

    _getCombination(product) {
        return (product.attribute_lines || []).flatMap(ptal => ptal.selected_attribute_value_ids);
    },

    _getParentsCombination(product) {
        let parentsCombination = [];
        for (const parentProductTmplId of product.parent_product_tmpl_ids || []) {
            const parentProduct = this._findProduct(parentProductTmplId);
            if (parentProduct) {
                parentsCombination.push(this._getCombination(parentProduct));
            }
        }
        return parentsCombination.flat();
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

    async _getOptionalProducts(product) {
        return this.rpc('/sale_product_configurator/get_optional_products', {
            product_template_id: product.product_tmpl_id,
            combination: this._getCombination(product),
            parent_combination: this._getParentsCombination(product),
            currency_id: this.props.currencyId,
            so_date: this.props.soDate,
            company_id: this.props.companyId,
            pricelist_id: this.props.pricelistId,
        });
    },

    async _getAlternateProducts(product) {
        return this.rpc('/sale_product_configurator/get_alternate_products', {
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
        const indexOptional = this.state.optionalProducts.findIndex(p => p.product_tmpl_id === productTmplId);
        const indexAccessory = this.state.accessoryProducts.findIndex(p => p.product_tmpl_id === productTmplId);
        const indexAlternate = this.state.alternateProducts.findIndex(p => p.product_tmpl_id === productTmplId);

        if (indexAlternate >= 0) {
            const alternateProduct = this.state.alternateProducts[indexAlternate];
            const newOptionalProducts = await this._getOptionalProducts(alternateProduct);
            const newAccessoryProducts = await this._getAccessoryProducts(alternateProduct);
            const newAlternateProducts = await this._getAlternateProducts(alternateProduct);

            this.state.products = [alternateProduct];
            this.state.optionalProducts = newOptionalProducts;
            this.state.accessoryProducts = newAccessoryProducts;
            this.state.alternateProducts = newAlternateProducts;
        }

        if (indexOptional >= 0) {
            const product = this._findProduct(productTmplId);
            this.state.products.push(...this.state.optionalProducts.splice(indexOptional, 1));
            const newOptionalProducts = await this._getOptionalProducts(product);
            if (newOptionalProducts) this.state.optionalProducts.push(...newOptionalProducts);
        }
        if (indexAccessory >= 0) {
            const product = this._findProduct(productTmplId);
            this.state.products.push(...this.state.accessoryProducts.splice(indexAccessory, 1));
            const newAccessoryProducts = await this._getAccessoryProducts(product);
            if (newAccessoryProducts) this.state.accessoryProducts.push(...newAccessoryProducts);
        }
    },

    async _removeProduct(productTmplId) {
        console.log(`Attempting to remove product with template ID: ${productTmplId}`);

        const index = this.state.products.findIndex(p => p.product_tmpl_id === productTmplId);
        if (index >= 0) {
            const product = this.state.products[index];
            this.state.products = this.state.products.filter(p => p.product_tmpl_id !== productTmplId);
            console.log(`Removed product from state.products:`, product);
            await this._handleProductRemoval(product, productTmplId);
            if (productTmplId !== this.props.productTemplateId) {
                return this._addProduct(this.props.productTemplateId);
            } else {
                return;
            }
        }

        const optionalIndex = this.state.optionalProducts.findIndex(p => p.product_tmpl_id === productTmplId);
        if (optionalIndex >= 0) {
            const product = this.state.optionalProducts[optionalIndex];
            this.state.optionalProducts = this.state.optionalProducts.filter(p => p.product_tmpl_id !== productTmplId);
            console.log(`Removed product from state.optionalProducts:`, product);
            await this._handleProductRemoval(product, productTmplId);
            return;
        }

        const accessoryIndex = this.state.accessoryProducts.findIndex(p => p.product_tmpl_id === productTmplId);
        if (accessoryIndex >= 0) {
            const product = this.state.accessoryProducts[accessoryIndex];
            this.state.accessoryProducts = this.state.accessoryProducts.filter(p => p.product_tmpl_id !== productTmplId);
            console.log(`Removed product from state.accessoryProducts:`, product);
            await this._handleProductRemoval(product, productTmplId);
            return;
        }

        console.error(`Product not found in any state array: ${productTmplId}`);
    },


    async _handleProductRemoval(product, productTmplId) {
        if (!product) {
            console.error(`Invalid product during removal handling: ${productTmplId}`);
            return;
        }

        console.log("Handling removal for product:", product);

        // Re-fetch optional products for the parent product
        const parentProductId = this.state.products[0]?.product_tmpl_id;
        const parentProduct = parentProductId ? this._findProduct(parentProductId) : null;

        const newOptionalProducts = parentProduct ? await this._getOptionalProducts(parentProduct) : [];
        const isOptionalProduct = newOptionalProducts.some(p => p.product_tmpl_id === productTmplId);

        if (isOptionalProduct) {
            this.state.optionalProducts = [...this.state.optionalProducts, product];
        } else {
            this.state.accessoryProducts = [...this.state.accessoryProducts, product];
        }

        // Remove child products
        const childProducts = this._getChildProducts(productTmplId) || [];
        for (const childProduct of childProducts) {
            if (!childProduct.parent_product_tmpl_ids.length) {
                await this._removeProduct(childProduct.product_tmpl_id);
            }
        }
    },


    _findProduct(productTmplId) {
        return this.state.products.find(p => p.product_tmpl_id === productTmplId) ||
            this.state.optionalProducts.find(p => p.product_tmpl_id === productTmplId) ||
            this.state.accessoryProducts.find(p => p.product_tmpl_id === productTmplId);
    },

    _getChildProducts(productTmplId) {
        return this.state.products.filter(p =>
            p.parent_product_tmpl_ids && p.parent_product_tmpl_ids.includes(productTmplId)
        );
    },
});

// Utility function for applying the product configuration
async function applyProduct(record, product) {
    if (!product || !product.attribute_lines) {
        return;
    }

    const customAttributesCommands = [
        x2ManyCommands.set([]),
    ];

    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            customAttributesCommands.push(
                x2ManyCommands.create(undefined, {
                    custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "unused"],
                    custom_value: ptal.customValue,
                })
            );
        }
    }

    const noVariantPTAVIds = product.attribute_lines
        .filter(ptal => ptal.create_variant === "no_variant")
        .flatMap(ptal => ptal.selected_attribute_value_ids);

    await record.update({
        product_id: [product.id, product.display_name],
        product_uom_qty: product.quantity,
        product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
        product_custom_attribute_value_ids: customAttributesCommands,
    });
}

// Patch SaleOrderLineProductField
patch(SaleOrderLineProductField.prototype, {
    async _openProductConfigurator(edit = false) {
        const saleOrderRecord = this.props.record.model.root;
        let ptavIds = this.props.record.data.product_template_attribute_value_ids.records.map(
            record => record.resId
        );
        let customAttributeValues = [];

        if (edit) {
            ptavIds = ptavIds.concat(this.props.record.data.product_no_variant_attribute_value_ids.records.map(
                record => record.resId
            ));
        }

        this.dialog.add(ProductConfiguratorDialog, {
            productTemplateId: this.props.record.data.product_template_id[0],
            ptavIds: ptavIds,
            customAttributeValues,
            quantity: this.props.record.data.product_uom_qty,
            productUOMId: this.props.record.data.product_uom[0],
            companyId: saleOrderRecord.data.company_id[0],
            pricelistId: saleOrderRecord.data.pricelist_id[0],
            currencyId: this.props.record.data.currency_id[0],
            soDate: serializeDateTime(saleOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                if (!mainProduct && optionalProducts.length) {
                    mainProduct = optionalProducts.shift();
                }
                await applyProduct(this.props.record, mainProduct);

                this._onProductUpdate();
                saleOrderRecord.data.order_line.leaveEditMode();

                for (const optionalProduct of optionalProducts) {
                    const line = await saleOrderRecord.data.order_line.addNewRecord({
                        position: 'bottom',
                        mode: "readonly",
                    });
                    await applyProduct(line, optionalProduct);
                }
            },
            discard: () => {
                saleOrderRecord.data.order_line.delete(this.props.record);
            },
        });
    },
});
