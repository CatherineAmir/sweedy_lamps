# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.date_utils import start_of, end_of, add
from odoo.tools.misc import format_date
import logging

LOGGER = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    manufacturing_period = fields.Selection(selection_add=[('weeks_of_month', 'Weeks Of Month')])

    def _get_date_range(self):
        self.ensure_one()
        date_range = []
        if self.manufacturing_period == 'weeks_of_month':
            first_day_month = start_of(fields.Date.today(), 'month')
            days_to_thursday = (3 - first_day_month.weekday()) % 7
            thursday = first_day_month + relativedelta(days=days_to_thursday)
            first_day = thursday - relativedelta(days=6)
            while first_day_month.month == thursday.month:
                date_range.append((first_day, thursday))
                first_day = add(thursday, days=1)
                thursday = thursday + relativedelta(days=7)

        else:
            date_range = super(Company, self)._get_date_range()

        return date_range

    def _date_range_to_str(self):
        date_range = self._get_date_range()
        dates_as_str = []
        lang = self.env.context.get('lang')
        if self.manufacturing_period == 'weeks_of_month':
            week_number = 1
            for date_start, date_stop in date_range:
                date_start_str = date_start.strftime('%d/%m')
                date_stop_str = date_stop.strftime('%d/%m')
                # dates_as_str.append(_('Week %s (%s to %s)') % (week_number,date_start_str,date_stop_str))
                dates_as_str.append(_('Week %s ') % (week_number) )
                week_number += 1
        else:
            dates_as_str = super(Company, self)._date_range_to_str()

        return dates_as_str
