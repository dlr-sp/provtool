import os
import pandas


def create_html_report(check_result, filename):
    with open(os.path.join(os.path.dirname(__file__), '..', 'templates/report.html'), 'r') as template_file,\
         open(filename, 'w') as report_file:
        template_content = template_file.read()

        rows = []
        for cr in check_result:
            used_by = ''
            if cr['used_by'] is not None:
                if type(cr['used_by']) == list:
                    used_by = '<br>'.join(cr['used_by'])
                else:
                    used_by = 'ERROR'
            template = '<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>' +\
                       '<td>{}</td><td>{}</td><td>{}</td>'
            rows.append(template.format(
                    cr['entity'],
                    cr['data'],
                    cr['name'],
                    cr['valid'],
                    used_by,
                    cr['activity'],
                    cr['start_time'],
                    cr['end_time']
            ))

        report_file.write(template_content.replace('###TABLE_CONTENT###', '<tr>{}</tr>'.
                          format('</tr>\n<tr>'.join(rows))))


def create_csv_report(check_result, filename):
    df = pandas.DataFrame(check_result)[['entity', 'data', 'name', 'valid', 'used_by',
                                         'activity', 'start_time', 'end_time']]
    df = df.explode('used_by').reset_index(drop=True)
    df.to_csv(filename, index=False)
