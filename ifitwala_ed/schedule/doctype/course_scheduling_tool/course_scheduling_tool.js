// Copyright (c) 2021, ifitwala and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course Scheduling Tool', {

  onload: function(frm) {
    frm.add_fetch('student_group', 'program', 'program');
    frm.add_fetch('student_group', 'course', 'course');
    frm.add_fetch('student_group', 'academic_year', 'academic_year');
    frm.add_fetch('student_group', 'academic_term', 'academic_term');
  },

  refresh: function(frm) {
    frm.disable_save();

    frm.page.set_primary_action(__('Schedule Course'), () => {
			frm.call('schedule_course')
				.then(r => {
					if (!r.message) {
						frappe.throw(__('There were errors creating Course Schedule'));
					}
					const { course_schedules } = r.message;
					if (course_schedules) {
						const html = `
						<table class="table table-bordered">
							<caption>${__('Following course schedules were created')}</caption>
							<thead><tr><th>${__("Course")}</th><th>${__("Date")}</th></tr></thead>
							<tbody>
								${course_schedules.map(
									c => `<tr><td><a href="#Form/School Event/${c.name}">${c.name}</a></td>
									<td>${c.schedule_date}</td></tr>`
								).join('')}
							</tbody>
						</table>`

						frappe.msgprint(html);
					}
				});
		});
  },

  student_group: function(frm) {
		frm.events.get_instructors(frm);
	},

	get_instructors: function(frm) {
		frm.set_value('instructors',[]);
		frappe.call({
			method: 'get_instructors',
			doc:frm.doc,
			callback: function(r) {
				if(r.message) {
					frm.set_value('instructors', r.message);
				}
			}
		})
	}
});
