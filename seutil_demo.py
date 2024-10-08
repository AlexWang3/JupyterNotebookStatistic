import dataclasses
import difflib
import json
from pathlib import Path
from typing import List, Tuple

import seutil as su


@dataclasses.dataclass
class RawData:
    old: List[str]
    new: List[str]
    commit_msg: str
    diff_seq: List[Tuple[str, int, int, int, int]]

    def concat_old_cells(self) -> str:
        return "\n".join(self.old)

    def concat_new_cells(self) -> str:
        return "\n".join(self.new)


def main():
    list1 = [
        "This is the first line.",
        "This is the second line.",
        "Here is another line.",
        "This is the line deleted",
        "This is the final line.",
    ]
    list2 = [
        "This is the first line.",
        "This is the second line.",
        "Here is another line.",
        "This is the final line.",
    ]

    diff_seq = difflib.SequenceMatcher(None, list1, list2).get_opcodes()

    data = RawData(old=list1, new=list2, commit_msg="", diff_seq=diff_seq)
    dataset = [data] * 5

    # save to jsonl
    su.io.dump(Path.cwd() / "raw-data-demo.jsonl", dataset)

    # # load from jsonl w/o seutil
    # with open(Path.cwd() / "raw-data-demo.jsonl", "r") as f:
    #     for line in f:
    #         data = json.loads(line)
    #         print(data)

    # load from jsonl w/ seutil
    dataset = su.io.load(Path.cwd() / "raw-data-demo.jsonl", clz=RawData)
    print(dataset)


if __name__ == "__main__":
    main()
