# -*- coding: utf-8 -*-
# Copyright (c) 2021, ifitwala and contributors
# For license information, please see license.txt

def get_filters_config():
	filters_config = {
		"fiscal year": {
			"label": "Fiscal Year",
			"get_field": "ifitwala_ed.accounting.utils.get_fiscal_year_filter_field",
			"valid_for_fieldtypes": ["Date", "Datetime", "DateRange"],
			"depends_on": "organization",
		}
	}

	return filters_config
