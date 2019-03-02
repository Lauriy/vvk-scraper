import codecs

import bs4
import requests

district_url_template = 'http://rk2015.vvk.ee/detailed-%s.html'
elected_members_url = 'http://rk2015.vvk.ee/elected-members.html'

elected_people = []
elected_members_response = requests.get(elected_members_url)
for elected_party_row in bs4.BeautifulSoup(elected_members_response.text, 'html.parser') \
        .select('.elected-party > tbody > tr'):
    for person_data in elected_party_row.select('td'):
        person_data_contents = person_data.contents[0]
        if person_data_contents != '\xa0':
            elected_people.append(person_data_contents)

results_file = codecs.open('results_rk2015.txt', 'w', 'utf-8')
results_file.write('number\tname\tdistrict\tparty\tvotes\tgot_mandate')
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
            candidate_got_mandate = candidate_name in elected_people
            results_file.write('\t'.join(
                [candidate_registration_number, candidate_name, str(i), current_party, candidate_total_votes,
                 str(candidate_got_mandate), '\n']))
results_file.close()
