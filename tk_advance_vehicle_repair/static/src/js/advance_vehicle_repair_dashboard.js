/** @odoo-module **/
import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {getDefaultConfig} from "@web/views/view";
import {useService} from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import {Domain} from "@web/core/domain";
import {sprintf} from "@web/core/utils/strings";

const {Component, useSubEnv, useState, onMounted, onWillStart, useRef} = owl;
import {loadJS, loadCSS} from "@web/core/assets"

class AdvanceVehicleDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            bookingStats: {'total_vehicle_booking': 0, 'vehicle_inspection': 0, 'vehicle_repair': 0, 'vehicle_inspection_repair': 0, 'booking_cancel': 0},
            inspectionJobCardStatus : {'total_inspection_job_card': 0, 'inspection_in_progress': 0, 'inspection_complete': 0, 'inspection_cancel': 0},
            repairJobCardStatus: {'x-axis': [], 'y-axis': []},
            bookingDetailsStatus: {'x-axis': [], 'y-axis': []},
            bookingSource: {'x-axis': [], 'y-axis': []},
            inspectionJobCardDetails: {'x-axis': [], 'y-axis': []},
            commonVehicleFuels: {'x-axis': [], 'y-axis': []},
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.repairJobCardStatus = useRef('vehicle_repair_job_card_details');
        this.bookingDetailsStatus = useRef('booking_details_graph');
        this.bookingSource = useRef('booking_source_graph');
        this.inspectionJobCardDetails = useRef('job_card_inspection_type');
        this.commonVehicleFuels = useRef('most_common_fuel_used_in_vehicle');

        onWillStart( async () => {
            await loadJS('/tk_advance_vehicle_repair/static/src/js/apexcharts.js');
            let bookingData = await this.orm.call('advance.vehicle.repair.dashboard', 'get_advance_vehicle_repair_dashboard', []);
            if(bookingData){
                this.state.bookingStats = bookingData;
                this.state.inspectionJobCardStatus = bookingData;
                this.state.repairJobCardStatus = {'x-axis': bookingData['repair_job_card_details'][0], 'y-axis': bookingData['repair_job_card_details'][1]}
                this.state.bookingDetailsStatus = {'x-axis': bookingData['booking_details'][0], 'y-axis': bookingData['booking_details'][1]}
                this.state.bookingSource = {'x-axis': bookingData['booking_source'][0], 'y-axis': bookingData['booking_source'][1]}
                this.state.inspectionJobCardDetails = {'x-axis': bookingData['inspection_job_card_details'][0], 'y-axis': bookingData['inspection_job_card_details'][1]}
                this.state.commonVehicleFuels = {'x-axis': bookingData['common_fuel_used_in_vehicle'][0], 'y-axis': bookingData['common_fuel_used_in_vehicle'][1]}
            }
        });
        onMounted(() => {
            this.renderRepairJobCardStatusGraph();
            this.renderBookingDetailsGraph();
            this.renderBookingSource();
            this.renderInspectionJobCardDetails();
            this.renderCommonVehicleFuels();
        })
    }

    renderRepairJobCardStatusGraph(){
        const options = {
            series: [
                {
                name: 'Status',
                data: this.state.repairJobCardStatus['y-axis'],
                }
            ],
            chart: {
                height: 400,
                type: 'bar',
            },
            colors: ['#f29e4c', '#f1c453', '#efea5a',  '#b9e769',  '#83e377', '#16db93', '#0db39e', '#048ba8', '#2c699a', '#54478c'],
            plotOptions: {
                bar: {
                    columnWidth: '10%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            xaxis: {
                categories: this.state.repairJobCardStatus['x-axis'],
                labels: {
                    style: {
                        colors: ['#000000'],
                        fontSize: '13px'}
                }
            }
        };
        this.renderGraph(this.repairJobCardStatus.el, options);
    }

    renderBookingDetailsGraph() {
        const options = {
            series: this.state.bookingDetailsStatus['y-axis'],
            chart: {
                type: 'pie',
                height: 410
            },
            dataLabels: {
                enabled: false
            },
            labels: this.state.bookingDetailsStatus['x-axis'],
            legend: {
                position: 'bottom',
            },
        };
        this.renderGraph(this.bookingDetailsStatus.el, options);
    }

    renderBookingSource(){
        const options = {
            series: [{
                name: 'Status',
                data: this.state.bookingSource['y-axis'],
            }],
            chart: {
                height: 400,
                type: 'bar',
            },
            colors: ['#2c699a', '#54478c'],
            plotOptions: {
                bar: {
                    columnWidth: '10%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            xaxis: {
                categories: this.state.bookingSource['x-axis'],
                labels: {
                    style: {
                        colors: ['#000000'],
                        fontSize: '13px'}
                }
            }
        };
        this.renderGraph(this.bookingSource.el, options);
    }

    renderInspectionJobCardDetails() {
        const options = {
            series: [{
                name: 'Status',
                data: this.state.inspectionJobCardDetails['y-axis'],
            }],
            chart: {
                height: 400,
                type: 'bar',
            },
            colors: ['#16db93', '#83e377', '#b9e769', '#efea5a', '#f1c453', '#f29e4c'],
            plotOptions: {
                bar: {
                    columnWidth: '10%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            xaxis: {
                categories: this.state.inspectionJobCardDetails['x-axis'],
                labels: {
                    style: {
                        colors: ['#000000'],
                        fontSize: '13px'}
                }
            }
        };
        this.renderGraph(this.inspectionJobCardDetails.el, options);
    }

    renderCommonVehicleFuels(){
        const options = {
            series: this.state.commonVehicleFuels['y-axis'],
            chart: {
                width: 500,
                height: 500,
                type: 'polarArea',
            },
            yaxis: {
                labels: {
                    formatter: function (val) {
                    return val.toFixed(0);
                    }
                },
            },
            dataLabels: {
                enabled:true,
            },
            labels: this.state.commonVehicleFuels['x-axis'],
            stroke: {
                colors: ['#fff']
            },
            fill: {
                opacity: 0.8
            },
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 200
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        };
        this.renderGraph(this.commonVehicleFuels.el, options);
       }

    renderGraph(el, options){
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    viewVehicleBooking(type){
        let domain,context;
        let name = this.getBookingStatus(type);
        if (type === 'all'){
            domain = []
        }else {
            domain = [['booking_stages', '=', type]]
        }
        context = { 'create':false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'vehicle.booking',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getBookingStatus(type){
        let name;
        if(type === 'all') {
            name = 'Bookings'
        }else if(type === 'vehicle_inspection') {
            name = 'In Inspections'
        }else if(type === 'vehicle_repair') {
            name = 'In Repairs'
        } else if(type === 'vehicle_inspection_repair') {
            name = 'In Inspections and Repairs'
        }else if(type === 'cancel') {
            name = 'Booking Cancelled'
        }
        return name;
    }

    viewInspectionJobCard(type){
        let domain,context;
        let name = this.getInspectionJobCardStatus(type);
        if (type === 'all'){
            domain = []
        }else {
            domain = [['stages', '=', type]]
        }
        context = { 'create':false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'inspection.job.card',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getInspectionJobCardStatus(type){
        let name;
        if(type === 'all') {
            name = 'Job Cards'
        }else if(type === 'b_in_progress') {
            name = 'Inspection In Progress'
        }else if(type === 'c_complete') {
            name = 'Inspection Completed'
        }else if(type === 'd_cancel') {
            name = 'Inspection Cancelled'
        }
        return name;
    }

}
AdvanceVehicleDashboard.template = "tk_advance_vehicle_repair.adv_dashboard";
registry.category("actions").add("advance_vehicle_repair_dashboard", AdvanceVehicleDashboard);