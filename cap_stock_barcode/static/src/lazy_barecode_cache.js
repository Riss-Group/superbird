/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import LazyBarcodeCache from '@stock_barcode/lazy_barcode_cache';

patch(LazyBarcodeCache.prototype, {
     _constructor() {
        super._constructor(...arguments);
    },
    setCache(cacheData) {
        for (const model in cacheData) {
            const records = cacheData[model];
                if (!this.dbIdCache.hasOwnProperty(model)) {
                this.dbIdCache[model] = {};
            }
            if (!this.dbBarcodeCache.hasOwnProperty(model)) {
                this.dbBarcodeCache[model] = {};
            }
                for (const record of records) {
                this.dbIdCache[model][record.id] = record;
                if (model === 'product.product' || model === 'product.template') {
                    const barcodes = record.barcode;
                    let barcodeArray = barcodes ? barcodes.split(',') : [];
                    for (const barcodeRecord of barcodeArray) {
                        const barcode = barcodeRecord;

                        if (!this.dbBarcodeCache[model][barcode]) {
                            this.dbBarcodeCache[model][barcode] = [];
                        }

                        if (!this.dbBarcodeCache[model][barcode].includes(record.id)) {
                            this.dbBarcodeCache[model][barcode].push(record.id);

                            if (this.nomenclature && this.nomenclature.is_gs1_nomenclature && this.gs1LengthsByModel[model]) {
                                this._setBarcodeInCacheForGS1(barcode, model, record);
                            }
                        }
                    }

                } else
                super.setCache(cacheData)
            }
        }
    }

});