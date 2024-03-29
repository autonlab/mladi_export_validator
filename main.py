"""
MLADI Export Validation Script
Usage: For usage instructions, run python main.py -h
"""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd

# TO-DO:
# - Validate that all files exist.

expected_file_suffixes = [
	'enum.csv',
	'enumeration.csv',
	'enumerationvalue.csv',
	'numeric.csv',
	'numericvalue.csv',
	'wave.csv',
	'wavesample.csv',
	'ce.csv',
	'cs_ce.csv',
	'cs.csv',
	'icd.csv',
	'lab.csv',
	'loc.csv',
	'meds.csv',
	'io.csv',
	'patient.csv',
  	'micro.csv',
	'suscep.csv',
	'dialysis_ce.csv',
	'dl_details_recent.csv',
	'surg.csv',
	'alert.csv',
	'demo.csv',
]

class Validator:

	def __init__(self, path, prefix):

		# Check that path exists, is a directory, and is not empty
		assert path.exists(), "Path does not exist: " + str(path)
		assert path.is_dir(), "Path is not a directory: " + str(path)
		assert any(path.iterdir()), "Path is empty: " + str(path)
		assert prefix[-1] != '_', "Prefix should not end in underscore: " + prefix

		self.path = path
		self.prefix = prefix

		# Build expected_filenames from prefix + expected_file_suffixes
		self.expected_filenames = [f"{prefix}_{suffix}" for suffix in expected_file_suffixes]

		# Get all files matching prefix + expected_file_suffixes
		self.all_matching_files = [file for file in path.glob(f"{prefix}*") if file.is_file()]

		# List all files which are both on disk (from all_matching_files) and expected (from expected_filenames)
		self.all_valid_files_on_disk = [file for file in self.all_matching_files if file.name in self.expected_filenames]

	def validate(self):
		"""
		Run all validation checks and print output. Return true if all checks pass, false otherwise.
		"""

		# Build a list of validator functions so we can run them in a loop
		validator_functions = [
			self.validate_filenames,
			self.validate_discharge_date,
			#self.validate_headers,
			self.validate_no_double_headers,
			self.validate_no_empty_dates,
		]

		num_errors = 0

		# Run each validator function in turn
		for validator_function in validator_functions:
			result = validator_function()
			if result == True:
				print("Passed")
			else:
				result_string = result if isinstance(result, str) else '\n'.join(result)
				print(f"Failed\n{result_string}")
				num_errors += 1
		
		# Print and return results
		if num_errors == 0:
			print("All tests passed.")
			return True
		else:
			print(f"{num_errors} tests failed.")
			return False

	def validate_discharge_date(self):

		print("Verifying discharge date...", end=' ')

		df = pd.read_csv(self.path / f"{self.prefix}_demo.csv", escapechar='\\', parse_dates=['DISCH_DATE'])

		# There is only one row. Get the DISCH_DATE value from the first row, and validate that it's between 2000 and the year of the current date
		discharge_date = df['DISCH_DATE'][0]
		if discharge_date.year < 2000 or discharge_date.year > pd.Timestamp.now().year:
			return [f"Discharge date is invalid: {discharge_date}"]
		else:
			return True

	
	def validate_filenames(self):
		"""
		Validate that all files in path have the expected filenames.
		:param path: Path to directory containing the exported files to validate (Path instance)
		:param prefix: Prefix for all files in directory (string)
		:return: True if all files are valid, list of error strings otherwise
		"""
		
		print("Verifying expected filenames...", end=' ')

		errors = []

		# List all files which are on disk (from all_matching_files) but not expected (from expected_filenames)
		unexpected_files_on_disk = [file for file in self.all_matching_files if file.name not in self.expected_filenames]

		# If there are unexpected files, return an error string listing the unexpected files
		if len(unexpected_files_on_disk) > 0:
			errors.append("Unexpected files found: " + ', '.join([file.name for file in unexpected_files_on_disk]))
		
		return errors if len(errors) > 0 else True

	def validate_no_double_headers(self):
		"""
		Validate that there are no double headers in any file.
		:return: True if all files are valid, list of error strings otherwise
		"""

		print("Verifying no double headers...", end=' ')

		errors = []
		
		# Open each file in all_valid_files_on_disk, and compare the first line to the second line.
		# If they are the same, return an error string listing the file.
		for file in self.all_valid_files_on_disk:
			with file.open() as f:
				first_line = f.readline()
				second_line = f.readline()
				if first_line == second_line:
					errors.append("Double header row found in file: " + file.name)

		return errors if len(errors) > 0 else True

	def validate_no_duplicate_lines(self):
		"""
		Validate that there are no duplicate lines in any file.
		"""
		
		print("Verifying no duplicate lines...", end=' ')

		errors = []

		# Open each file in all_valid_files_on_disk, and compare each line to the previous line.
		# If they are the same, return an error string listing the file.
		for file in self.all_valid_files_on_disk:
			with file.open() as f:
				previous_line = None
				for line in f:
					if line == previous_line:
						errors.append("Duplicate line found in file: " + file.name)
					previous_line = line

		return errors if len(errors) > 0 else True

	def validate_no_empty_dates(self):
		"""
		Validate that there are no empty dates in EHR files.
		"""

		print("Verifying no empty dates...", end=' ')

		file_columns_to_check = {
			'ce': ['DATE'],
			'cs': ['FORM_DATE'],
			'cs_ce': ['date'],
			'demo': ['REG_DATE', 'DISCH_DATE'],
			'icd': ['DATE'],
			'io': ['DATE'],
			'lab': ['EVENT_DATE', 'VALID_DATE'],
			'loc': ['BEG_DATE', 'END_DATE'],
			'meds': ['CHART_DATE'],
			'patient': ['Timestamp'],
		}

		errors = []

		for file_suffix, cols in file_columns_to_check.items():
			try:
				df = pd.read_csv(self.path / f"{self.prefix}_{file_suffix}.csv", escapechar='\\')
			except Exception as e:
				errors.append(f"Error reading {self.prefix}_{file_suffix}.csv: {e}")
				continue
			for col in cols:
				if len(np.where(pd.isnull(df[col]))[0]) > 0:
					errors.append(f"Empty dates found in {col} column of {self.prefix}_{file_suffix}.csv")

		return errors if len(errors) > 0 else True



def main():

	# Read in command-line arguments "path" and "prefix", both of which are required.
	# If prefix does not end in underscore, add underscore.
	parser = argparse.ArgumentParser()
	parser.add_argument("path", help="Path to directory containing the exported files to validate")
	parser.add_argument("prefix", default=None, nargs='*', help="Prefix for all files in directory")
	args = parser.parse_args()
	
	# Validate filenames
	path = Path(args.path)
	prefix = args.prefix

	# Initial printout
	print()
	print(f"Path is: {path}")
	print(f"Prefix is: {prefix if prefix else '[not provided / test all patients in folder]'}")

	# Assemble list of prefixes to test
	if prefix is None or len(prefix) == 0:
		prefixes = set(['_'.join(str(p).split('/')[-1].split('_')[:2]) for p in path.glob('*.csv')])
	else:
		assert type(prefix) == list, "Prefix must be a list of strings"
		assert len(prefix) > 0, "Prefix must be a non-empty list of strings"
		prefixes = prefix

	print()
	failed_patients = []
	for	prefix in list(prefixes):
		prefix = prefix.strip('_')
		print(f"Testing patient {prefix} in {path}")
		validator = Validator(path, prefix)
		passed = validator.validate()
		if not passed:
			failed_patients.append(prefix)
		print()

	print("Summary\n-------")
	if len(failed_patients) == 0:
		print("All patients passed.")
	else:
		print(f"{len(failed_patients)} patients failed: {', '.join(failed_patients)}")
	print()

if __name__ == "__main__":
	main()
