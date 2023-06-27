"""
MLADI Export Validation Script
Usage: For usage instructions, run python main.py -h
"""

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

def validate_filenames(path, prefix):
	"""
	Validate that all files in path have the expected filenames.
	:param path: Path to directory containing the exported files to validate (Path instance)
	:param prefix: Prefix for all files in directory (string)
	:return: True if all files are valid, list of error strings otherwise
	"""
    
	print("Verifying expected filenames...", end=' ')

	errors = []

	# Build expected_filenames from prefix + expected_file_suffixes
	expected_filenames = [prefix + suffix for suffix in expected_file_suffixes]
	print('\n'.join(expected_filenames))

	# Check if path exists
	if not path.exists():
		errors.append("Path does not exist: " + str(path))
		return errors
	
	# Check if path is a directory
	if not path.is_dir():
		errors.append("Path is not a directory: " + str(path))
		return errors
	
	# Check if path is empty
	if not any(path.iterdir()):
		errors.append("Path is empty: " + str(path))
		return errors
	
	# Check if any files exist other than those in expected_filenames.
	# Only check the files in path which begin with prefix.
	for file in path.glob(f"{prefix}*"):
		if file.is_file():
			if file.name not in expected_filenames:
				errors.append("Unexpected file found: " + file.name)

	if len(errors) == 0:
		return True
	else:
		return errors

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

	results = validate_filenames(path, prefix)
	print("Passed" if results==True else "Failed\n" + '\n'.join(results), end="\n\n")


if __name__ == "__main__":
	main()
