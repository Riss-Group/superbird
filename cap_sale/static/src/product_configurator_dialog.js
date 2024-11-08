/** @odoo-module */

import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { serializeDateTime } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { WarningDialog } from "@web/core/errors/error_dialogs";

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
            const { products, optional_products, accessory_products, alternate_products } = await this._loadPartData(this.props.edit);
            this.state.accessoryProducts = accessory_products;
            this.state.alternateProducts = alternate_products;
        });
    },

    _getCombination(product) {
        return (product.attribute_lines || []).flatMap(ptal => ptal.selected_attribute_value_ids);
    },


    _getParentsCombination(product) {
        let parentsCombination = [];
        for (const parentProductTmplId of product.parent_product_tmpl_ids || []) {
            const parentProduct = this._findProduct(parentProductTmplId);
            if (parentProduct) {  // Ensure parentProduct is defined
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
        const indexOptional = this.state.optionalProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
        const indexAccessory = this.state.accessoryProducts.findIndex(
            p => p.product_tmpl_id === productTmplId
        );
		const indexAlternate = this.state.alternateProducts.findIndex(
			p => p.product_tmpl_id === productTmplId
		);

		if (indexAlternate >= 0) {
				const productToReplace = this.state.products[0]; 
				const alternateProduct = this.state.alternateProducts[indexAlternate];
				
				// Generate alternate product's Optional/Accessory/Alternate Products
				let newOptionalProducts = await this._getOptionalProducts(alternateProduct);
				let newAccessoryProducts = await this._getAccessoryProducts(alternateProduct);
				let newAlternateProducts = await this._getAlternateProducts(alternateProduct);

				console.log(alternateProduct);

				// Replace the original product in the products array
				this.state.products = [alternateProduct];

				// Update optional, accessory, and alternate products
				this.state.accessoryProducts = newAccessoryProducts;
				this.state.alternateProducts = newAlternateProducts;
				this.state.optionalProducts = newOptionalProducts;
			}

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

    async _removeProduct(productTmplId) {
        const index = this.state.products.findIndex(p => p.product_tmpl_id === productTmplId);
		console.log("hit 1");
        if (index >= 0) {
            const product = this.state.products.splice(index, 1)[0];
			const parent_product = this.state.products[0]?.product_tmpl_id;
			console.log(parent_product);
            const findProduct = this._findProduct(parent_product);
			console.log(findProduct);
            let newOptionalProducts = await this._getOptionalProducts(findProduct);
    
            const isOptionalProduct = newOptionalProducts.some(p => p.product_tmpl_id === productTmplId);
            if (isOptionalProduct) {
				console.log(isOptionalProduct);
				console.log("hit 3");
                this.state.optionalProducts.push(product);
            } else {
				console.log("hit 4");
                this.state.accessoryProducts.push(product);
            }
    
            for (const childProduct of this._getChildProducts(productTmplId)) {
                childProduct.parent_product_tmpl_ids = childProduct.parent_product_tmpl_ids.filter(
                    id => id !== productTmplId
                );
				console.log("hit 5");
                if (!childProduct.parent_product_tmpl_ids.length) {
                    this._removeProduct(childProduct.product_tmpl_id);
                    this.state.optionalProducts.splice(
                        this.state.optionalProducts.findIndex(
                            p => p.product_tmpl_id === childProduct.product_tmpl_id
                        ), 1
                    );
					console.log("hit 5");
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

// Utility function for applying the product configuration
async function applyProduct(record, product) {
    console.log(record);
    console.log(product);

    // handle custom values & no variants
    const customAttributesCommands = [
        x2ManyCommands.set([]),  // Command.clear isn't supported in static_list/_applyCommands
    ];
    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            customAttributesCommands.push(
                x2ManyCommands.create(undefined, {
                    custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "we don't care"],
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

// Patch the SaleOrderLineProductField with your custom logic
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

            customAttributeValues =
                this.props.record.data.product_custom_attribute_value_ids.records[0]?.isNew
                    ? this.props.record.data.product_custom_attribute_value_ids.records.map(record => record.data)
                    : await this.orm.read(
                        'product.attribute.custom.value',
                        this.props.record.data.product_custom_attribute_value_ids.currentIds,
                        ["custom_product_template_attribute_value_id", "custom_value"]
                    );
        }

        this.dialog.add(ProductConfiguratorDialog, {
            productTemplateId: this.props.record.data.product_template_id[0],
            ptavIds: ptavIds,
            customAttributeValues: customAttributeValues.map(
                data => {
                    return {
                        ptavId: data.custom_product_template_attribute_value_id[0],
                        value: data.custom_value,
                    };
                }
            ),
            quantity: this.props.record.data.product_uom_qty,
            productUOMId: this.props.record.data.product_uom[0],
            companyId: saleOrderRecord.data.company_id[0],
            pricelistId: saleOrderRecord.data.pricelist_id[0],
            currencyId: this.props.record.data.currency_id[0],
            soDate: serializeDateTime(saleOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                // CUSTOM LOGIC: If main product is undefined, use the first optional product
                if (!mainProduct && optionalProducts) {
                    mainProduct = optionalProducts[0];
                    optionalProducts.shift();  // Remove the main product from the optional products list
                }

                console.log("Main Product:", mainProduct);
                console.log("Optional Products:", optionalProducts);

                // Apply product logic
                await applyProduct(this.props.record, mainProduct);

                this._onProductUpdate();
                saleOrderRecord.data.order_line.leaveEditMode();

                // Apply optional products
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
