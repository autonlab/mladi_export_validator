from pathlib import Path
import argparse

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

		self.path = Path(path)
		self.prefix = prefix

		# Check that path exists, is a directory, and is not empty
		assert path.exists(), "Path does not exist: " + str(path)
		assert path.is_dir(), "Path is not a directory: " + str(path)
		assert any(path.iterdir()), "Path is empty: " + str(path)

		# Build expected_filenames from prefix + expected_file_suffixes
		self.expected_filenames = [prefix + suffix for suffix in expected_file_suffixes]

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
			#self.validate_headers,
			self.validate_no_double_headers,
		]

		num_errors = 0

		# Run each validator function in turn
		for validator_function in validator_functions:
			result = validator_function()
			if result == True:
				print("Passed")
			else:
				print("Failed")
				num_errors += 1
			
		
		# Print and return results
		if num_errors == 0:
			print("All tests passed.")
			return True
		else:
			print(f"{num_errors} tests failed.")
			return False

	def validate_filenames(self):
		"""
		Validate that all files in path have the expected filenames.
		:param path: Path to directory containing the exported files to validate (Path instance)
		:param prefix: Prefix for all files in directory (string)
		:return: True if all files are valid, error string otherwise
		"""
		
		print("Verifying expected filenames...", end=' ')

		errors = []

		# List all files which are on disk (from all_matching_files) but not expected (from expected_filenames)
		unexpected_files_on_disk = [file for file in self.all_matching_files if file.name not in self.expected_filenames]

		# If there are unexpected files, return an error string listing the unexpected files
		if len(unexpected_files_on_disk) > 0:
			return "Unexpected files found: " + ', '.join([file.name for file in unexpected_files_on_disk])
		
		# If there are no unexpected files, return true
		return True

	def validate_headers(self):
		"""
		Validate that all files in path have the expected headers.
		"""

		print("Verifying expected filenames [CHECK NOT BUILD YET]...", end=' ')
		return True

	def validate_no_double_headers(self):
		"""
		Validate that there are no double headers in any file.
		"""

		print("Verifying no double headers...", end=' ')
		
		# Open each file in all_valid_files_on_disk, and compare the first line to the second line.
		# If they are the same, return an error string listing the file.
		for file in self.all_valid_files_on_disk:
			with file.open() as f:
				first_line = f.readline()
				second_line = f.readline()
				if first_line == second_line:
					return "Double header row found in file: " + file.name

def main():

	# Read in command-line arguments "path" and "prefix", both of which are required.
	# If prefix does not end in underscore, add underscore.
	parser = argparse.ArgumentParser()
	parser.add_argument("path", help="Path to directory containing the exported files to validate")
	parser.add_argument("prefix", help="Prefix for all files in directory")
	args = parser.parse_args()

	# Validate prefix
	if not args.prefix.endswith('_'):
		args.prefix += '_'
	
	# Validate filenames
	path = Path(args.path)
	prefix = args.prefix

	validator = Validator(path, prefix)
	_ = validator.validate()


if __name__ == "__main__":
	main()