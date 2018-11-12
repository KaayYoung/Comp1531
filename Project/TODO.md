Documentation:
- UML class diagram with attributes
- Front sheet - need signatures


Approved:
- Worklog
- User stories


(done) Unit tests for:

1) Create questions
- Create mandatory question -> assert question exists and is mandatory
- Create optional question -> assert question exists and is optional
- Create mandatory question with empty text -> assert error
- Create optional question with empty text -> assert error
- Create a question with unspecified mandatory/optional flag -> assert error
- Create a mandatory question with same text as an existing mandatory question -> assert error
- Create an optional question with same text as an existing optional question -> assert error
- Create a mandatory question with same text as an existing optional question -> assert both questions were created

2) Create a survey
- Create a survey with 0 questions -> assert error
- Create a survey with duplicate questions -> assert error
- Create a survey with no associated course offering -> assert error
- Create a survey with 3 mandatory and 3 optional questions of varying MCQ and text types -> assert survey exists with associated questions
- Create a survey for the same course offering -> assert error
- Survey that is created goes into review phase -> assert newly created survey is in review phase
- Survey that is successfully reviewed becomes open -> assert reviewed survey in open phase

3) Enrol a student
- Enrol a student with no associated course offering -> assert error
- Enrol a student with a course offering -> assert student has one course offering
- Enrol a student with multiple course offerings -> assert student has multiple course offerings

4) User authentication
- User with correct credentials -> assert check_login returns true
- User with incorrect credentials -> assert check_login returns false
- Student user is identified as a student -> assert student function property returns true
- Staff user is identified as a staff -> assert staff function property returns true
- Admin user is identified as an admin -> assert admin function property returns true
- Guest user is identified as a guest -> assert guest function property returns true

5) Survey student responses
- Only logged in student users can complete the survey -> assert not logged in users and staff or admin cannot complete a survey
- Survey response must have all mandatory questions completed -> if not assert error. If so assert response stored
- Responses not associated with student -> get response and assert no data connected to user is stored
- Student response for non-existent survey -> assert error