/** @odoo-module **/
const { Component, useState } = owl
import { registry } from "@web/core/registry";

export class ProductModal extends Component {
    static template = 'ProductModalTemplate';

	async willStart() {
		this.data = await this._loadProducts;
	}

    setup() {
        this.state = useState({
			alternateProducts:[],
			optionalProducts:[],
			accessoryProducts:[],
        });
		// this._loadProducts;
    }

    // Update startDate and endDate based on the selected range
    async _loadProducts() {
		let alternateProducts = [];
		let optionalProducts = [];
		let accessoryProducts = [];

		const products = await this.env.services.rpc('/web/dataset/call_kw/product.template/cap_get_products', {
			model: 'product.template',
			method: 'cap_get_products',
			args: [],
			kwargs: {},
		});
		console.log(products)
    }

   //  async loadData() {
   //      try {
   //          const wos = await this.env.services.rpc('/web/dataset/call_kw/mrp.workorder/cap_get_workorder_data', {
   //              model: 'mrp.workorder',
   //              method: 'cap_get_workorder_data',
   //              args: [startDate, endDate, this.state.operations],
			// 	kwargs: {},
   //          });
			//
			// console.log(wos);
			//
			// this.state.workorders = wos;
   //      } catch (error) {
   //          console.error("Error during RPC call:", error);
   //      }
   //  }
}

// Register the component as a client action
registry.category('actions').add('product_modal', ProductModal);


