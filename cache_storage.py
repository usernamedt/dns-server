import logging
from time import time

import jsonpickle as jsonpickle
from tinydb import Query, TinyDB
from tinydb.operations import set

from dns_message import DnsMessage
from dns_record import DnsRecord


class CacheStorage:
    """
    Provides functionality to interact with cache database,
    create new cache entries, add/delete answers
    """

    def __init__(self, cache_dir, db_name='cache.json'):
        db = TinyDB(cache_dir / db_name)
        self.entries = db.table('cache_entries')
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup()

    def cleanup(self) -> None:
        for entry in self.entries.all():
            self.refresh_cache(entry["id"])

    def refresh_cache(self, entry_id):
        entry = self._get_entry(entry_id)
        if not entry:
            return
        for raw_answer in entry["answers"]:
            answer = jsonpickle.decode(raw_answer)
            if answer.ttl + answer.recv_time < time():
                entry["answers"].remove(raw_answer)
                self.__save_field(entry_id, "answers", entry["answers"])

    def add_entry(self, dns_message: DnsMessage):
        records = dns_message.ans_records + dns_message.add_records + dns_message.auth_records
        for answer in records:
            self._add_record(answer)

    def _add_record(self, record: DnsRecord):
        if len(record.rec_data.val) == 0 or record.ans_type > 2:
            return
        entry_id = self._get_entry_id(record.name.val, record.ans_type)
        entry = self._get_entry(entry_id)
        json_record = jsonpickle.encode(record)
        if not entry:
            self.entries.insert({"id": entry_id, "answers": [json_record]})
        else:
            entry["answers"].append(json_record)
            self.__save_field(entry_id, "answers", entry["answers"])

    def _get_entry(self, id):
        Entry = Query()
        return self.entries.get(Entry.id == id)

    @staticmethod
    def _get_entry_id(name, r_type):
        return f"{name}#{r_type}"

    def get_answers(self, name, r_type):
        entry_id = self._get_entry_id(name, r_type)
        self.refresh_cache(entry_id)
        entry = self._get_entry(entry_id)
        if not entry:
            return None
        result = []
        for answer in entry["answers"]:
            decoded_answer: DnsRecord = jsonpickle.decode(answer)
            decoded_answer.ttl = decoded_answer.ttl - (time() - decoded_answer.recv_time)
            result.append(decoded_answer)
        return result

    def __save_field(self, entry_id, field_name, value) -> None:
        Entry = Query()
        logging.info(f"Updating {entry_id} field {field_name} with value "
                     f"{value}")
        self.entries.update(set(field_name, value), Entry.id == entry_id)
