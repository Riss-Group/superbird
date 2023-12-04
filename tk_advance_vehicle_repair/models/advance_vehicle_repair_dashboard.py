# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AdvanceVehicleRepairDashboard(models.Model):
    """Advance Vehicle Repair Dashboard"""
    _name = "advance.vehicle.repair.dashboard"
    _description = __doc__

    @api.model
    def get_advance_vehicle_repair_dashboard(self):
        total_vehicle_booking = self.env['vehicle.booking'].sudo().search_count([])
        vehicle_inspection = self.env['vehicle.booking'].sudo().search_count(
            [('booking_stages', '=', 'vehicle_inspection')])
        vehicle_repair = self.env['vehicle.booking'].sudo().search_count([('booking_stages', '=', 'vehicle_repair')])
        vehicle_inspection_repair = self.env['vehicle.booking'].sudo().search_count(
            [('booking_stages', '=', 'vehicle_inspection_repair')])
        booking_cancel = self.env['vehicle.booking'].sudo().search_count([('booking_stages', '=', 'cancel')])

        total_inspection_job_card = self.env['inspection.job.card'].sudo().search_count([])
        inspection_in_progress = self.env['inspection.job.card'].sudo().search_count([('stages', '=', 'b_in_progress')])
        inspection_complete = self.env['inspection.job.card'].sudo().search_count([('stages', '=', 'c_complete')])
        inspection_cancel = self.env['inspection.job.card'].sudo().search_count([('stages', '=', 'd_cancel')])

        repair_job_card = self.env['repair.job.card'].sudo().search_count([])
        assign_to_technician = self.env['repair.job.card'].sudo().search_count(
            [('stages', '=', 'assign_to_technician')])
        in_diagnosis = self.env['repair.job.card'].sudo().search_count([('stages', '=', 'in_diagnosis')])
        supervisor_inspection = self.env['repair.job.card'].sudo().search_count(
            [('stages', '=', 'supervisor_inspection')])
        hold = self.env['repair.job.card'].sudo().search_count([('stages', '=', 'hold')])
        complete = self.env['repair.job.card'].sudo().search_count([('stages', '=', 'complete')])
        cancel = self.env['repair.job.card'].sudo().search_count([('stages', '=', 'cancel')])

        booking_source_direct = self.env['vehicle.booking'].sudo().search_count([('booking_source', '=', 'direct')])
        booking_source_website = self.env['vehicle.booking'].sudo().search_count([('booking_source', '=', 'website')])

        inspection_job_card_full_inspection = self.env['inspection.job.card'].sudo().search_count(
            [('inspection_type', '=', 'full_inspection')])
        inspection_job_card_specific_inspection = self.env['inspection.job.card'].sudo().search_count(
            [('inspection_type', '=', 'specific_inspection')])

        repair_job_card_details = [
            ['Job Cards', 'Assign to Technician', 'In Diagnosis', 'Supervisor Inspection', 'Hold', 'Completed',
             'Cancelled'],
            [repair_job_card, assign_to_technician, in_diagnosis, supervisor_inspection, hold, complete, cancel]]

        booking_details = [['Vehicle Inspection', 'Vehicle Repair', 'Vehicle Inspection and Repair'],
                           [vehicle_inspection, vehicle_repair, vehicle_inspection_repair]]

        booking_source = [['Direct', 'Website'], [booking_source_direct, booking_source_website]]

        inspection_job_card_details = [['Full Inspection', 'Specific Inspection'],
                                       [inspection_job_card_full_inspection, inspection_job_card_specific_inspection]]

        data = {
            'total_vehicle_booking': total_vehicle_booking,
            'vehicle_inspection': vehicle_inspection,
            'vehicle_repair': vehicle_repair,
            'vehicle_inspection_repair': vehicle_inspection_repair,
            'booking_cancel': booking_cancel,
            'total_inspection_job_card': total_inspection_job_card,
            'inspection_in_progress': inspection_in_progress,
            'inspection_complete': inspection_complete,
            'inspection_cancel': inspection_cancel,
            'repair_job_card_details': repair_job_card_details,
            'booking_details': booking_details,
            'booking_source': booking_source,
            'inspection_job_card_details': inspection_job_card_details,
            'common_fuel_used_in_vehicle': self.get_most_common_fuels(),
        }
        return data

    def get_most_common_fuels(self):
        top_five_fuel = {}
        for group in self.env['vehicle.booking'].read_group([], ['vehicle_fuel_type_id'], ['vehicle_fuel_type_id'],
                                                            orderby="vehicle_fuel_type_id DESC"):
            fuel_type = self.env['vehicle.fuel.type'].sudo().browse(int(group['vehicle_fuel_type_id'][0])).name
            top_five_fuel[fuel_type] = group['vehicle_fuel_type_id_count']
        top_five_fuel = dict(sorted(top_five_fuel.items(), key=lambda item: item[1], reverse=True))
        return [list(top_five_fuel.keys()), list(top_five_fuel.values())]
