import codecs

import bs4
import requests

district_url_template = 'http://rk2015.vvk.ee/detailed-%s.html'
mandate_method_url = 'http://rk2015.vvk.ee/acquired-mandates.html'

mandate_methods_response = requests.get(mandate_method_url)
parsed_mandate_methods_response = bs4.BeautifulSoup(mandate_methods_response.text, 'html.parser')
methods_to_candidates_map = {}
for i, mandate_type_table in enumerate(parsed_mandate_methods_response.select('table.mandates')):
    if i == 0:
        mandate_type = 'personal'
    elif i == 1:
        mandate_type = 'district'
    else:
        mandate_type = 'compensation'
    methods_to_candidates_map[mandate_type] = []
    for candidate_row in mandate_type_table.select('tr')[1:]:
        candidate_name = candidate_row.select('td')[6].contents[0]
        methods_to_candidates_map[mandate_type].append(candidate_name)

results_file = codecs.open('results_rk2015.txt', 'w', 'utf-8')
results_file.write('number\tname\tdistrict\tparty\tvotes\tmandate_method')
results_file.write('\n')
for i in range(1, 13):
    response = requests.get(district_url_template % i)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    area_parties_results = soup.select('.detailed-party')
    for area_party_results in area_parties_results:
        current_party = area_party_results.select('.party-name')[0].contents[0]
        party_row_data = area_party_results.select('tbody tr')
        for candidate_index, candidate_data in enumerate(party_row_data):
            if current_party != 'Üksikkandidaadid' and candidate_index == len(party_row_data) - 1:
                continue
            candidate_registration_number = candidate_data.select('td')[1].contents[0]
            candidate_name = candidate_data.select('td')[2].contents[0]
            candidate_total_votes = candidate_data.select('td > strong')[0].contents[0]
            candidate_mandate_method = None
            if candidate_name in methods_to_candidates_map['personal']:
                candidate_mandate_method = 'personal'
            elif candidate_name in methods_to_candidates_map['district']:
                candidate_mandate_method = 'district'
            elif candidate_name in methods_to_candidates_map['compensation']:
                candidate_mandate_method = 'compensation'
            else:
                candidate_mandate_method = None
            results_file.write('\t'.join(
                [candidate_registration_number, candidate_name, str(i), current_party, candidate_total_votes,
                 str(candidate_mandate_method), '\n']))
results_file.close()
