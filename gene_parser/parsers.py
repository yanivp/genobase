supported_file_types = ['fasta', 'csv']


class ParsedResult:
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence

    def __str__(self):
        return '{}:{}'.format(self.name, self.sequence)


class ParserBuffer:
    """Simple DNA text buffer/parser"""

    def __init__(self, parser_type):
        self.buffer = list()
        if parser_type == 'fasta':
            self.parse = self._parse_as_fasta
        elif parser_type == 'csv':
            self.parse = self._parse_as_csv
        else:
            raise NotImplemented('Parser for `{}` is not implemented'.format(parser_type))

    def _parse_as_fasta(self, first_result, file_done):
        """Parse buffer as a FASTA structure"""

        if file_done or self.buffer.count('>') > 1:
            buffer_str = ''.join(self.buffer)
            parts = buffer_str.split('>')

            parsed_results = list()

            last_part = (0 if file_done else 1)
            for part in parts[0:len(parts) - last_part]:
                if part == '':
                    continue

                parsed_results.append(
                    ParsedResult(
                        name=part[:part.find('\n')].replace('\n', ''),
                        sequence=part[part.find('\n'):].replace('\n', '')
                    )
                )

            if not file_done:
                self.buffer = self.buffer[len(self.buffer) - len(parts[len(parts) - 1]):]

            return parsed_results

        return None

    def _parse_as_csv(self, first_result, file_done):
        """Parse buffer as a CSV structure"""

        if file_done or self.buffer.count('\n') > 0:
            buffer_str = ''.join(self.buffer)
            parts = buffer_str.split('\n')

            parsed_results = list()

            last_part = (0 if file_done else 1)
            for part in parts[0:len(parts) - last_part]:
                if part == '':
                    continue

                if not first_result:
                    parsed_results.append(
                        ParsedResult(
                            name=part[:part.find(',')].replace('\r', ''),
                            sequence=part[part.find(',') + 1:].replace('\r', '')
                        )
                    )

                first_result = False

            if len(parsed_results) > 0 and not file_done:
                self.buffer = self.buffer[len(self.buffer) - len(parts[len(parts) - 1]):]

            return parsed_results

        return None
