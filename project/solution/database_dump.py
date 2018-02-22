from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, Boolean
import pandas
import os
import csv
from datetime import datetime

club_ready_column_mapping = {
		0: "member_id",
		1: "studio_key",
		2: "class_tag",
		3: "instructor_full_name",
		4: "level",
		5: "canceled",
		6: "class_time",
		7: "checked_in_at"
}
mbo_reservations_column_mapping = {
		0: "member_id",
		1: "studio_key",
		2: "studio_address_street",
		3: "studio_address_city",
		4: "studio_address_state",
		5: "studio_address_zip",
		6: "class_tag",
		7: "viewed_at",
		8: "reserved_at",
		9: "canceled_at",
		10: "class_time",
		11: "checked_in_at"
}

def create_table(engine, table_csv):
	table_name = table_csv.split('.csv')[0]
	table_csv = os.path.join("data", table_csv)
	with engine.connect() as con:
		if not con.dialect.has_table(con, table_name):
			df = pandas.read_csv(table_csv, sep=',')
			df.to_sql(con=con, name=table_name)

def transform_club_ready_row(row):
	transformed_row = {}
	for i in range(min(len(row), len(club_ready_column_mapping))):
		transformed_row[club_ready_column_mapping[i]] = row[i]
	validate_row(transformed_row)
	return transformed_row

def transform_mbo_reservations_row(row):
	transformed_row = {}
	for i in range(min(len(row), len(mbo_reservations_column_mapping))):
		transformed_row[mbo_reservations_column_mapping[i]] = row[i]
	if transformed_row["canceled_at"]:
		transformed_row["canceled"] = True
	else:
		transformed_row["canceled"] = False
	validate_row(transformed_row)
	return transformed_row

def validate_row(row_dict):
	if row_dict["canceled"] == 'f':
		row_dict["canceled"] = False
	elif row_dict["canceled"] == 't':
		row_dict["canceled"] = True

	# Verify values in columns where we expect datetimes
	timestamp_columns = ["viewed_at", "reserved_at", "canceled_at", "class_time", "checked_in_at"]
	for col in timestamp_columns:
		ts_string = row_dict.get(col)
		if ts_string == "":
			row_dict[col] = None
		elif ts_string:
			try:
				datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S")
			except ValueError as e:
				print("Error: {} for column {}".format(e, col))
				row_dict[col] = None

	# Verify values in columns where we expect integers
	integer_columns = ["member_id", "level"]
	for col in integer_columns:
		if row_dict.get(col) is not None:
			try:
				row_dict[col] = int(row_dict[col])
			except ValueError as e:
				print("Value {} for column {} is not an integer".format(row_dict[col], col))
				row_dict[col] = None

def csv_data_to_db(res_table, con):
	for filename in os.listdir('data'):
		with open(os.path.join("data", filename)) as csvfile:
			reader = csv.reader(csvfile)
			counter = 0
			for row in reader:
				counter += 1
				if counter == 1:
					continue
				if "club-ready" in filename:
					table_row = transform_club_ready_row(row)
				elif "mbo-reservations" in filename:
					table_row = transform_mbo_reservations_row(row)
				else:
					print("Schema unknown for this file {}. Skipping".format(filename))
				insert_statement = res_table.insert().values(**table_row)
				try:
					con.execute(insert_statement)
				except Exception as e:
					print(e)

def create_reservations_table(con):
	metadata = MetaData()
	reservations_table = Table("reservations", metadata,
							Column("member_id", Integer),
							Column("studio_key", String),
							Column("class_tag", String),
							Column("level", Integer),
							Column("instructor_full_name", String),
							Column("viewed_at", DateTime),
							Column("reserved_at", DateTime),
							Column("canceled_at", DateTime),
							Column("canceled", Boolean),
							Column("class_time", DateTime),
							Column("checked_in_at", DateTime),
							Column("studio_address_street", String),
							Column("studio_address_city", String),
							Column("studio_address_state", String),
							Column("studio_address_zip", String))
	metadata.create_all(con)
	return reservations_table

def main():
	engine = create_engine("postgresql://localhost:5432/reservationsdb")

	with engine.connect() as con:
		reservations_table = create_reservations_table(con)
		csv_data_to_db(reservations_table, con)

if __name__ == "__main__":
	main()
