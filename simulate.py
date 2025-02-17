from user_data.doraneko94.module import FighterA, FighterB
from core import SensorData
from enum import IntEnum
import time, random
import multiprocessing

class Command(IntEnum):
    Exit = 0
    Request = 1
    Response = 2

class Unit(IntEnum):
    Fighter1A = 0
    Fighter1B = 1
    Missile1A = 2
    Missile1B = 3
    Fighter2A = 4
    Fighter2B = 5
    Missile2A = 6
    Missile2B = 7

class State:
    def __init__(self, state):
        self.states = [state for _ in range(8)]

def model_update(unit, conn, unit_enum):
    try:
        msg = conn.recv()
    except EOFError:
        return True
    if msg.get("command") == Command.Exit:
        return True
    if msg.get("command") == Command.Request:
        sensor_data = SensorData(
            x = msg.get("x"),
            y = msg.get("y"),
            t = msg.get("t"),
            sensor = msg.get("sensor")
        )
        time.sleep(random.uniform(0.0, 2.0)) #
        f, a = unit.update(sensor_data)
        response = {"unit": unit_enum, "command": Command.Response, "f": f, "a": a}
        conn.send(response)
    return False

def process_f1a(conn):
    unit = FighterA()
    while True:
        if model_update(unit, conn, Unit.Fighter1A):
            break
    conn.close()

def process_f1b(conn):
    unit = FighterB()
    while True:
        if model_update(unit, conn, Unit.Fighter1B):
            break
    conn.close()

def environment(conns, procs, n=8):
    internal_state = 0
    t = 0
    pending = State(None)
    awaiting = State(False)
    active = State(True)

    while internal_state < 10:
        for i in range(n):
            if active.states[i] and not procs[i].is_alive():
                print(f"Process {Unit(i).name} terminated unexpectedly.")
                active.states[i] = False
                awaiting.states[i] = False

        for i in range(n):
            if active.states[i] and not awaiting.states[i]:
                try:
                    request = {
                        "command": Command.Request, "x": 0, "y": 0, "t": t, "sensor": []
                    }
                    conns[i].send(request)
                    awaiting.states[i] = True
                except Exception as e:
                    print(f"Error sending to {Unit(i).name}:", e)
                    active.states[i] = False
        
        start_time = time.time()
        while True:
            now = time.time()
            elapsed = now - start_time

            for i in range(n):
                if active.states[i] and awaiting.states[i] and conns[i].poll():
                    try:
                        response = conns[i].recv()
                        pending.states[i] = response
                        awaiting.states[i] = False
                    except Exception as e:
                        print(f"Error sending to {Unit(i).name}:", e)
                        active.states[i] = False
                        awaiting.states[i] = False

            if not any(active.states):
                break

            if elapsed >= 1.0:
                break

            time.sleep(0.01)

        for i in range(n):
            if pending.states[i] is not None:
                internal_state += pending.states[i]["f"]
        print(internal_state)
        
        t += 1
    
    for i in range(n):
        if active.states[i]:
            try:
                conns[i].send({"command": Command.Exit})
            except Exception as e:
                print(f"Error sending exit to {Unit(i).name}:", e)
    print("Termination condition met. Exiting enviroment.")

if __name__ == "__main__":
    parent_conn_f1a, child_conn_f1a = multiprocessing.Pipe()
    parent_conn_f1b, child_conn_f1b = multiprocessing.Pipe()

    proc_f1a = multiprocessing.Process(target=process_f1a, args=(child_conn_f1a,))
    proc_f1b = multiprocessing.Process(target=process_f1b, args=(child_conn_f1b,))

    proc_f1a.start()
    proc_f1b.start()

    try:
        environment([parent_conn_f1a, parent_conn_f1b], [proc_f1a, proc_f1b], n=2)
    finally:
        proc_f1a.join()
        proc_f1b.join()