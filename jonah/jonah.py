import argparse
import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    headers = [i for i, v in enumerate(df.iloc[:, 0] == 'Vendor') if v]
    # make sub tables from header_i to header_(i+1) - 1 with header_i as header
    tables = [df.iloc[headers[i]:headers[i + 1]] for i in range(len(headers) - 1)]
    # turn the first row into the header
    tables = [table.rename(columns=table.iloc[0]).iloc[1:] for table in tables]

    # for each table delete every row where "PO Number" is NaN
    tables = [table.dropna(subset=['PO Number']) for table in tables]

    # under vendors, each table should have one non nan value (in the first row)
    # which is the vendor name and the rest nan, so we can fillna with the vendor name
    # only fill the vendors column
    filled_tables = []
    for table in tables:
        vendor = table['Vendor'].dropna().iloc[0]
        table.loc[:, 'Vendor'] = vendor
        filled_tables.append(table)

        # check that all the headers are the same
    headers = [table.columns for table in filled_tables]
    for i in range(len(headers) - 1):
        assert headers[i].equals(headers[i + 1])

    df = pd.concat(filled_tables)
    return df


def compare_spreadsheets(s1: pd.DataFrame, s2: pd.DataFrame) -> pd.DataFrame:
    output_order = cols = ['Vendor', 'new_vendor', 'PO Number', 'new_po', 'Cost Code', 'new_cc',
                           'Approved Purchase Orders (A)', 'apo_diff',
                           'Approved Change Orders (B)', 'aco_diff', 'Total Committed (C = A + B)', 'tc_diff',
                           'Invoiced (D)', 'invoiced_diff', 'Balance Remaining (E = C - D)', 'br_diff']


def make_new_item_row(old_row, new_vendor=False, new_po=False, new_cc=False):
    assert new_vendor or new_po or new_cc, 'At least one of new_vendor, new_po, or new_cc must be True'
    row = old_row.to_dict()
    row['new_vendor'] = new_vendor
    row['new_po'] = new_vendor or new_po
    row['new_cc'] = new_vendor or new_po or new_cc
    return row


def compare(s1: pd.DataFrame, s2: pd.DataFrame) -> pd.DataFrame:
    output_order = ['Vendor', 'new_vendor', 'PO Number', 'new_po', 'Cost Code', 'new_cc',
                    'Approved Purchase Orders (A)', 'apo_diff',
                    'Approved Change Orders (B)', 'aco_diff', 'Total Committed (C = A + B)', 'tc_diff',
                    'Invoiced (D)', 'invoiced_diff', 'Balance Remaining (E = C - D)', 'br_diff']

    vendors_1 = set(s1.Vendor)
    pos_1 = {v: set(s1[s1.Vendor == v]['PO Number']) for v in vendors_1}

    diff_cols = {
        'Approved Purchase Orders (A)': 'apo_diff',
        'Approved Change Orders (B)': 'aco_diff',
        'Total Committed (C = A + B)': 'tc_diff',
        'Invoiced (D)': 'invoiced_diff',
        'Balance Remaining (E = C - D)': 'br_diff'
    }

    diff = []
    for row in s2.iloc:

        # case 1: new vendor
        vendor = row['Vendor']
        if vendor not in vendors_1:
            diff.append(make_new_item_row(row, new_vendor=True))
            continue

        # case 2: existing vendor, new po
        po = row['PO Number']
        if po not in pos_1[vendor]:
            diff.append(make_new_item_row(row, new_po=True))
            continue

        # case 3: existing vendor and po, new cost code
        cc = row['Cost Code']
        if cc not in set(s1[(s1.Vendor == vendor) & (s1['PO Number'] == po)]['Cost Code']):
            diff.append(make_new_item_row(row, new_cc=True))
            continue

        # case 4: existing vendor, po, and cost code
        # find rows in s1 that match the current row vendor, po, and cost code
        match = s1[(s1.Vendor == vendor) & (s1['PO Number'] == po) & (s1['Cost Code'] == cc)]
        # make sure the match is unique
        assert len(match) == 1, f'Expected 1 match, got {len(match)} for {vendor=}, {po=}, {cc=}'

        row = row.to_dict()
        row['new_vendor'] = False
        row['new_po'] = False
        row['new_cc'] = False
        match = match.iloc[0].to_dict()
        for k, v in diff_cols.items():
            row[v] = row[k] - match[k]
        diff.append(row)

    diff = pd.DataFrame(diff)
    return diff[output_order]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--old', type=str, help='Path to the old spreadsheet')
    parser.add_argument('-n', '--new', type=str, help='Path to the new spreadsheet')
    parser.add_argument('-out', '--output', type=str, help='Path to the output generated spreadsheet (default diff.csv)', default='diff.csv')
    args = parser.parse_args()

    s1 = pd.read_excel(args.original)
    s2 = pd.read_excel(args.new)

    s1 = clean(s1)
    s2 = clean(s2)

    comparison_df = compare_spreadsheets(s1, s2)
    comparison_df.to_csv(args.output, index=False)


if __name__ == '__main__':
    main()
