## ETL Architecture Project Questionnaire

### Project Data Points
1. Across all reservation partners for January & February, how many completed reservations occurred?
	Query: "select count(checked_in_at) from reservations where checked_in_at >= '2018-01-01 00:00:00' and checked_in_at < '2018-03-01 00:00:00';"
	A: 135

2. Which studio has the highest rate of reservation abandonement (did not cancel but did not check-in)?
	Query: "select studio_key, count(*) as abandonment_rate from reservations where canceled=false and checked_in_at is null group by studio_key order by abandonment_rate desc;"
	A: 3-way tie between: orlando-yoga, crossfit-control-jacksonville-beach, and hive-athletics (each with 3 abandoned reservations)

3. Which fitness area (i.e., tag) has the highest number of completed reservations for February
	Query: "select class_tag, count(*) from reservations where checked_in_at >= '2018-02-01 00:00:00' and checked_in_at < '2018-03-01 00:00:00' group by class_tag order by count desc;"
	A: Yoga with 12 completed reservations for February

4. How many members completed at least 1 reservation and had no more than 1 canceled reservation in January?
	Query: "select count(*) from (select member_id from (select member_id, count(*) from reservations where canceled=true and class_time >= '2018-01-01 00:00:00' and class_time < '2018-02-01 00:00:00' group by member_id) canceled_classes where count <= 1) C intersect select * from (select member_id from reservations where checked_in_at >= '2018-01-01 00:00:00' and checked_in_at < '2018-02-01 00:00:00' group by member_id) A;"
	A: 6

	Breakdown of query:
		"select count(*) from C intersect A";
		Table C: "select member_id from (select member_id, count(*) from reservations where canceled=true and class_time >= '2018-01-01 00:00:00' and class_time < '2018-02-01 00:00:00' group by member_id) canceled_classes where count <= 1"
		Table C is the member_id's for members who canceled no more than one reservation in the month of January
		Table A: "select member_id from reservations where checked_in_at >= '2018-01-01 00:00:00' and checked_in_at < '2018-02-01 00:00:00' group by member_id"
		Table A is the member_id's for members who completed at least one reservation in the month of January
		The intersect of these two tables gives us the member_ids who completed 1 reservation and had no more than 1 cancelation in January

### Project Discussion
1. Describe what custom logic you chose to implement in your ETL solution and why?
	The two main pieces of logic were mapping the columns of the two different formats of csvs to the columns for the reservations table. I made sure I was storing all the information, even if it wasn't in both csvs (like the address of the studio) to make sure I wasn't losing any data, and I made sure that column names that described the same thing in the two different csv schema were mapped to the same column name (i.e. "checked_in_at" and "signed_in_at"). 
	The other data transformation was to check that all the data points were of the correct type/format for the corresponding column. This was easy for strings, integers, and booleans, but slightly more involved for any column with a timestamp. I used python's datetime.strptime function to ensure that every timestamp fit the correct format and printed an error if it didn't. 

2. What forecasting opportunities do you see with a dataset like this and why?
	We can see which types of exercise are most popular, which have highest retention (member comes back multiple times). We can have a good idea of where the best engagement is, and can try to include more classes of these types. We can also see trends over days/weeks/months and see if completed reservations are overall increasing, and at what rate. We can get a breakdown of which days of the week/times are most popular, which instructors are the best, which areas of the country have the most engagement, and allocate resources accordingly. 

3. What other data would you propose we gather to make reporting/forecasting more robust and why?
	It's likely you're already doing this, but data about the members like age, gender, how they were referred or the company they're associated with, etc. To be able to tie specific behaviors with member attributes can be helpful for forecasting future behaviors. Collecting more data on the classes like class duration, average class size, or the distance from the member's workplace to the class could be helpful for forecasting which classes have highest attendance rates. Information about the studio itself could be helpful, such as when the studio joined Peerfit, to be able to see the rate of growth of member usage of a particular studio.  

4. What was difficult and how might you have approached that obstacle differently next time?
	Some of the data involving date/times was a bit challenging. I opted to get rid of any datetime strings that were malformed, like "2018-01-" or "09:30:00". To make this a bit more robust I would try to infer datetimes based on other datetimes in the row. For example, in the column of club-ready-reservations_01-2018.csv where reserved_for="09:30:00", I saw that signed_in_at="2018-01-09 09:27:36". I could've used this to infer that reserved_for="2018-01-09 09:30:00" but I decided to forgo these inferences for the purposes of this project. 
