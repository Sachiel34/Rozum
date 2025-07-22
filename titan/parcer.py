import json
import math

class Parcer:
    """
    Загрузка и обработка команд из JSON-файла 'titan.json'.
    Атрибуты:
        json_data      — словарь, загруженный из JSON;
        dict_algorithm — список команд из body[0]['subCommands'];
        dict_points    — список точек из points;
        offset_table   — словарь смещений по id точек.
    """

    def __init__(self, json_path: str, offset_table: dict = None):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)
        self.offset_table = offset_table or {}
        self.dict_algorithm = self.json_data['body'][0]['subCommands']
        self.dict_points = self.json_data['points']

    def move(self, command: dict) -> dict:
        """Обработка команд типов MOVE, GRIPPER, WAIT, OFFSET."""
        t = command.get("type")

        if t == "MOVE":
            cmd = {
                "motion": command["motion"],
                "blend": command["blend"],
                "points": []
            }
            for sub in command["subCommands"]:
                if sub["type"] == "POINT":
                    for pt in self.dict_points:
                        if pt["id"] == sub["pointId"]:
                            new_pt = dict(pt)
                            # Применяем смещение, если задано
                            if pt["id"] in self.offset_table:
                                dx, dy, dz = self.offset_table[pt["id"]]
                                base_pos = pt["position"][:3]
                                base_rot = pt["position"][3:]
                                new_pos = [p + d for p, d in zip(base_pos, (dx, dy, dz))]
                                new_pt["position"] = new_pos + base_rot
                            cmd["points"].append(new_pt)
            return cmd

        if t == "GRIPPER":
            return {
                "motion": "joint",
                "blend": 0,
                "points": [{"gripper": int(command["value"])}]
            }

        if t == "WAIT":
            return {
                "motion": "wait",
                "blend": 0,
                "points": [{"wait": int(command["time"])}]
            }

        if t == "OFFSET":
            for pt in self.dict_points:
                if pt["id"] == command["pointId"]:
                    pos = pt["position"][:3]
                    rot = pt["position"][3:]
                    offset = command["offset"]
                    new_pos = [p + o for p, o in zip(pos, offset)]
                    return {
                        "motion": "linear",
                        "blend": 0,
                        "points": [{
                            "position": new_pos + rot,
                            "pose": pt["pose"],
                            "id": f"{pt['id']}_offset"
                        }]
                    }

        # На случай неизвестных типов
        return {}

    def process_list(self) -> list:
        """
        Собирает algorithm_list:
        - группирует команды LOOP и одиночные MOVE/GRIPPER/WAIT/OFFSET
        - конвертирует углы из радиан в градусы
        """
        algorithm_list = []

        for cmd in self.dict_algorithm:
            ctype = cmd.get("type")
            if ctype == "LOOP":
                count = cmd.get("repeatCount") or cmd.get("count", 1)
                block = [count]
                for sub in cmd["subCommands"]:
                    if sub["type"] in ("MOVE", "GRIPPER", "WAIT", "OFFSET"):
                        block.append(self.move(sub))
                algorithm_list.append(block)

            elif ctype in ("MOVE", "GRIPPER", "WAIT", "OFFSET"):
                algorithm_list.append([1, self.move(cmd)])

        # Преобразование углов (позиции[3:6]) из радиан в градусы
        for block in algorithm_list:
            for cmd in block[1:]:
                for pt in cmd.get("points", []):
                    if "position" in pt:
                        for i in range(3, 6):
                            pt["position"][i] = pt["position"][i] * 180 / math.pi

        return algorithm_list


