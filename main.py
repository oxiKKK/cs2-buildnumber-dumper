#
# cs2 buildnumber dumper
#
# (c) 2023 oxiKKK
#

import sys
import os
import re

# pattern to be searched for:
#
# .rdata:00000001803FEE88 41 70 72 00                   aApr_0 db 'Apr',0             ; DATA XREF: .rdata:00000001803C2388↑o
# .rdata:00000001803FEE88                                                             ; .rdata:00000001803FEEE8↓o
# .rdata:00000001803FEE8C 4D 61 72 00                   aMar_0 db 'Mar',0             ; DATA XREF: .rdata:00000001803C2380↑o
# .rdata:00000001803FEE8C                                                             ; .rdata:00000001803FEEE0↓o
# .rdata:00000001803FEE90 4A 75 6E 00                   aJun_0 db 'Jun',0             ; DATA XREF: .rdata:00000001803C2398↑o
# .rdata:00000001803FEE90                                                             ; .rdata:00000001803FEEF8↓o
# .rdata:00000001803FEE94 4D 61 79 00                   aMay_0 db 'May',0             ; DATA XREF: .rdata:00000001803C2390↑o
# .rdata:00000001803FEE94                                                             ; .rdata:00000001803C23F0↑o
# .rdata:00000001803FEE94                                                             ; .rdata:00000001803FEEF0↓o
# .rdata:00000001803FEE98 53 65 70 20 31 33 20 32 30 32+aSep132023 db 'Sep 13 2023',0 ; DATA XREF: build_number+38↑o
# pattern = b'Apr\0Mar\0Jun\0May\0'
pattern = b'2023\0'

# remove the first element of sys.argv, which is the script name
file_paths = sys.argv[1:]

# HL1 release date. Valve uses this as a starting point to calculate the amount of days from this particular
# date u till now as a build number for their engine-
RELEASE_DATE = 34995  # Oct 24 1996


def is_engine2_dll(file_path):
    """
    check whenever the input file is engine2.dll.
    we only use this file in order to get the build number.
    """

    # Get the base name of the file (i.e., the file name without the directory)
    file_name = os.path.basename(file_path)

    # Check if the file name is "engine2.dll" (case-sensitive)
    return file_name == "engine2.dll"


# List of month abbreviations
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Days in each month
month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def build_number(date_utf8):  # expected 9842 for 'Oct  5 2023'
    """
    converts a date-like string into a cs2-like build number.
    expects date_utf8 to be MMM DD YYYY
    """

    # Extract month, day, and year
    current_month, current_day, current_year = date_utf8.split()

    # Unpack as integers
    m = months.index(current_month)
    d = 0
    y = 0

    for i in range(m):
        d += month_days[i]

    d += int(current_day) - 1
    y = int(current_year) - 1900

    d = d + int((y - 1) * 365.25)

    # Adjust for leap years
    if ((y % 4) == 0) and m > 1:
        d += 1

    # Adjust for the base date
    d -= RELEASE_DATE

    return d


def main():
    # check for amount of arguments
    if len(sys.argv) <= 1:
        return

    print(f"searching for: {pattern}.")

    for file in file_paths:
        # check for input file
        if not is_engine2_dll(file):
            return

        try:
            with open(file, 'rb') as exe_file:
                binary_data = exe_file.read()
        except:
            print(f"error: file {file} not found.")
            return

        if binary_data:
            # find the pattern inside the file
            pos = binary_data.find(pattern)
            if (pos == -1):
                print(f"{file}: could not find pattern.")
                return

            # we should be able to find a string such as:
            #  MMM DD YYYY
            date_start = pos - 7
            date = binary_data[date_start:date_start + 11]
            try:
                date_utf8 = date.decode('utf-8')
            except:
                print(f"error: could not decode {date_utf8} as utf-8.")
                return

            # see if it is actually a date
            match = re.match(
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s{1,2}\d{1,2}\s\d{4}$', date_utf8)

            if not match:
                print(
                    f"error: date '{date_utf8}' not recognized as a valid date.")
                return

            # now compute build number
            buildnum = build_number(date_utf8)

            print(
                f"found at {file}!0x{pos:016X}: '{date_utf8}' -> build {buildnum}")


if __name__ == "__main__":
    main()
