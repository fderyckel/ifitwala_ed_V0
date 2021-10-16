// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Website Theme', {
	validate(frm) {
		let theme_scss = frm.doc.theme_scss;
		if (theme_scss && theme_scss.includes('frappe/public/scss/website')
			&& !theme_scss.includes('ifitwala_ed/public/scss/website')
		) {
			frm.set_value('theme_scss',
				`${frm.doc.theme_scss}\n@import "ifitwala_ed/public/scss/website";`);
		}
	}
});
