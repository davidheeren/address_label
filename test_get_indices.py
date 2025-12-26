import unittest
import pandas
from main import get_indices
from io import StringIO


class TestGetIndices(unittest.TestCase):
    def setUp(self):
        """Set up a DataFrame from CSV data for testing."""
        csv_data = """John Walker,ACME Cars,231 Stark Hollow Road,,Greeley,CO,12345
Billy and Bob Walker,ACME Cars,232 Stark Hollow Road,,Greeley,CO,12345
Cindi Fry,ACME Cars,233 Stark Hollow Road,,Greeley,CO,12345
Rafael Monaghan,ACME Cars,234 Stark Hollow Road,,Greeley,CO,12345
Ernesto Maldanado,ACME Cars,235 Stark Hollow Road,,Greeley,CO,12345
Elda Gurney,ACME Cars,236 Stark Hollow Road,,Greeley,CO,12345
Eleanor Steller,ACME Cars,237 Stark Hollow Road,,Greeley,CO,12345
Jean Mantle,ACME Cars,238 Stark Hollow Road,,Greeley,CO,12345
Jude Wishon,ACME Cars,239 Stark Hollow Road,,Greeley,CO,12345
Joselyn Viruet,ACME Cars,240 Stark Hollow Road,,Greeley,CO,12345
Lesa Kindig,ACME Cars,241 Stark Hollow Road,,Greeley,CO,12345
Lyn Klinger,ACME Cars,242 Stark Hollow Road,,Greeley,CO,12345
Craig Walker,ACME Cars,243 Stark Hollow Road,,Greeley,CO,12345
Tennie Otten,ACME Cars,244 Stark Hollow Road,,Greeley,CO,12345
Cira Trowell,ACME Cars,245 Stark Hollow Road,,Greeley,CO,12345
Madalene Raatz,ACME Cars,246 Stark Hollow Road,,Greeley,CO,12345
Darleen Mccluskey,ACME Cars,274 Stark Hollow Road,,Greeley,CO,12345
Ayesha Nevius     ,ACME Cars,248 Stark Hollow Road,,Greeley,CO,12345
"""
        # Consistent with get_dataframe which uses header=None for CSVs
        self.df = pandas.read_csv(StringIO(csv_data), header=None)
        # df has 18 rows, indexed 0-17
        self.row_offset = 1  # As returned by get_dataframe for CSV

    def test_empty_filter(self):
        self.assertEqual(get_indices("", self.df, self.row_offset), set())

    def test_wildcard_filter(self):
        self.assertEqual(get_indices("*", self.df, self.row_offset), set(range(18)))

    def test_single_digit(self):
        self.assertEqual(get_indices("2", self.df, self.row_offset), {1})

    def test_multiple_digits(self):
        self.assertEqual(get_indices("1, 5, 10", self.df, self.row_offset), {0, 4, 9})

    def test_simple_range(self):
        self.assertEqual(get_indices("5-9", self.df, self.row_offset), {4, 5, 6, 7, 8})

    def test_combined_filter(self):
        self.assertEqual(get_indices("1, 5-7, 15", self.df, self.row_offset), {0, 4, 5, 6, 14})

    def test_inversion(self):
        """Test inverting a single number after selecting all."""
        self.assertEqual(get_indices("*, !5", self.df, self.row_offset), set(range(18)) - {4})

    def test_inverted_range(self):
        """Test inverting a range after selecting all."""
        self.assertEqual(get_indices("*, !5-9", self.df, self.row_offset), set(range(18)) - {4, 5, 6, 7, 8})

    def test_inversion_without_base(self):
        """Test that inverting from an empty set results in an empty set."""
        self.assertEqual(get_indices("!5", self.df, self.row_offset), set())

    def test_inverted_range_without_base(self):
        """Test that inverting a range from an empty set results in an empty set."""
        self.assertEqual(get_indices("!5-9", self.df, self.row_offset), set())

    def test_complex_filter(self):
        self.assertEqual(get_indices("1, 5-9, !7, 15", self.df, self.row_offset), {0, 4, 5, 7, 8, 14})

    def test_overlapping_filters(self):
        self.assertEqual(get_indices("1-5, 3-7", self.df, self.row_offset), {0, 1, 2, 3, 4, 5, 6})

    def test_empty_parts(self):
        self.assertEqual(get_indices("1,,5", self.df, self.row_offset), {0, 4})

    def test_dangling_inversion(self):
        with self.assertRaisesRegex(Exception, "Invalid filter: dangling '!'"):
            get_indices("!", self.df, self.row_offset)

    def test_invalid_range_alpha(self):
        with self.assertRaisesRegex(Exception, "Not a valid filter: a-b"):
            get_indices("a-b", self.df, self.row_offset)

    def test_invalid_range_mixed_alpha_numeric(self):
        with self.assertRaisesRegex(Exception, "Not a valid filter: 1-ab"):
            get_indices("1-ab", self.df, self.row_offset)
        with self.assertRaisesRegex(Exception, "Not a valid filter: ab-1"):
            get_indices("ab-1", self.df, self.row_offset)

    def test_invalid_range_dangling_hyphens(self):
        with self.assertRaisesRegex(Exception, "Invalid index range: -"):
            get_indices("-", self.df, self.row_offset)
        with self.assertRaisesRegex(Exception, "Invalid index range: 1-"):
            get_indices("1-", self.df, self.row_offset)
        with self.assertRaisesRegex(Exception, "Invalid index range: -1"):
            get_indices("-1", self.df, self.row_offset)

    def test_invalid_range_too_many_parts(self):
        with self.assertRaisesRegex(Exception, "Invalid index range: 5-7-9"):
            get_indices("5-7-9", self.df, self.row_offset)

    def test_invalid_range_start_gt_end(self):
        with self.assertRaisesRegex(Exception, "Invalid range: start > end in 9-5"):
            get_indices("9-5", self.df, self.row_offset)

    def test_name_filter_single_hit(self):
        self.assertEqual(get_indices("Cindi Fry", self.df, self.row_offset), {2})

    def test_name_filter_multiple_hits(self):
        self.assertEqual(get_indices("Walker", self.df, self.row_offset), {0, 1, 12})

    def test_name_filter_case_insensitive(self):
        self.assertEqual(get_indices("cindi fry", self.df, self.row_offset), {2})

    def test_name_filter_partial_name(self):
        self.assertEqual(get_indices("Bob", self.df, self.row_offset), {1})

    def test_name_filter_multiple_parts(self):
        self.assertEqual(get_indices("Bob Walker", self.df, self.row_offset), {1})

    def test_name_filter_no_match(self):
        self.assertEqual(get_indices("No Such Name", self.df, self.row_offset), set())

    def test_name_filter_with_inversion(self):
        self.assertEqual(get_indices("Walker, !Craig", self.df, self.row_offset), {0, 1})

    def test_name_filter_with_trailing_spaces(self):
        self.assertEqual(get_indices("Ayesha Nevius", self.df, self.row_offset), {17})

    def test_combined_name_and_index_filter(self):
        self.assertEqual(get_indices("Walker, 1-3", self.df, self.row_offset), {0, 1, 2, 12})

    def test_combined_name_and_index_filter_with_inversion(self):
        self.assertEqual(get_indices("Walker, !1", self.df, self.row_offset), {1, 12})

    def test_index_out_of_bounds_single_low(self):
        with self.assertRaisesRegex(Exception, "Invalid index: 0, out of bounds 1-18"):
            get_indices("0", self.df, self.row_offset)

    def test_index_out_of_bounds_single_high(self):
        with self.assertRaisesRegex(Exception, "Invalid index: 19, out of bounds 1-18"):
            get_indices("19", self.df, self.row_offset)

    def test_index_out_of_bounds_range_low(self):
        with self.assertRaisesRegex(Exception, "Invalid index: 0-5, out of bounds 1-18"):
            get_indices("0-5", self.df, self.row_offset)

    def test_index_out_of_bounds_range_high(self):
        with self.assertRaisesRegex(Exception, "Invalid index: 15-19, out of bounds 1-18"):
            get_indices("15-19", self.df, self.row_offset)


if __name__ == "__main__":
    unittest.main()
