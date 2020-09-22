This modules is to set up

* __Student.__  
  * The student doctype has all the demographics associated with a particular student. 
  * The student name is also the link to many other documents (courses, assessments, health record, etc.)
  * Once a student is created, it will automatically create a related user with website permission.  
* __Guardian.__  The adults responsible for the student.  This isn't necessary for colleges and higher education institution.  It can then serve as the person to contact in case of emergency.  
  * All demographics associated with a particular student.  
  * The student is used to link the guardian to his/her child.  
  * Once a guardian record is created, the system will create an associated user. This is for the guardian to be able to consult all of its child(ren) records.  The guardian is then a website user with login (do not have access to the desk)
* __Student Guardian.__  This is a child table to link the student with his/her guardian. 
* __Guardian Student.__  This is a child table to link the Guardian with his/her child/ren. This child table is automatically created once the the student guardian has been filled. 
* __Student Log.__ 
  * To record annecdotal story about a student. This can be related to academic, behavior, social/emotional well-being or something else. 


