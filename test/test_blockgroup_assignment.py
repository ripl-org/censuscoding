import os
import pandas as pd
import unittest

from censuscoding import censuscode

project_dir = os.path.dirname(os.path.abspath(__file__))

censuscode(
  os.path.join(project_dir, "data", "test-addresses.csv"),
  os.path.join(project_dir, "data", "test-addresses-out.csv")
)

censuscoded_dat = pd.read_csv(
  os.path.join(project_dir, "data", "test-addresses-out.csv")
)

print("Match rate of", len(censuscoded_dat)/200)

class GetsValidBlockgroups(unittest.TestCase):

    def test_blockgroups_nonmissing(self):
      self.assertEqual(
        censuscoded_dat['blkgrp'].isnull().values.any(), 
        False, 
        'Some values missing blockgroups'
      )
    
    def test_zip_nonmissing(self):
      self.assertEqual(
        censuscoded_dat['zip_code'].isnull().values.any(), 
        False,
        'Some values missing zip codes'
      )
    
    def test_recordid_nonmissing(self):
      self.assertEqual(
        censuscoded_dat['record_id'].isnull().values.any(), 
        False,
        'Some values missing record ids'
      )

[
  os.remove(x) for x in
  [
    os.path.join(project_dir, "data", "test-addresses-out.csv"),
    os.path.join(project_dir, "data", "test-addresses-out.csv.log")
  ]
]
