import random

random.seed(42)

def gen_score():
    r = random.random()
    if r < 0.08:
        return random.randint(30, 54)
    elif r < 0.18:
        return random.randint(55, 68)
    else:
        return random.randint(70, 99)

# B students & courses
b_students = [f"16B{i:03d}" for i in range(1, 51)]

b_lines = []
for i, sid in enumerate(b_students):
    base = (i % 10) + 101
    for k in range(5):
        num = base + k
        if num <= 110:
            cid = f"16B{num}"
        else:
            cid = f"16B{101 + (num - 111)}"
        s = gen_score()
        b_lines.append(f"('{cid}', '{sid}', '{s}', '16', 'B')")

# C course selection pattern (same as upload_hw4.sql)
c_pattern = [
    [101,102,105,107,109],[101,104,105,109,110],[102,103,106,108,110],
    [101,104,106,107,109],[102,105,107,108,110],[101,103,105,109,110],
    [102,104,106,108,109],[101,105,107,109,110],[102,103,105,107,108],
    [101,104,106,109,110],[102,105,107,108,110],[101,103,104,109,110],
    [102,104,106,107,109],[101,105,106,108,110],[102,103,105,107,109],
    [101,104,106,108,110],[102,105,107,109,110],[101,103,104,107,109],
    [102,106,108,109,110],[101,105,107,108,110],[102,103,105,107,109],
    [101,104,106,108,110],[102,105,107,109,110],[101,103,104,107,109],
    [102,104,106,108,110],[101,105,106,107,109],[102,103,105,108,110],
    [101,104,106,109,110],[102,105,107,108,109],[101,103,105,107,110],
    [102,104,106,108,109],[101,105,107,109,110],[102,103,105,107,108],
    [101,104,106,109,110],[102,105,107,108,110],[101,103,104,107,109],
    [102,104,106,108,110],[101,105,106,107,109],[102,103,105,108,110],
    [101,104,106,109,110],[102,105,107,108,109],[101,103,105,107,110],
    [102,104,106,108,109],[101,105,107,109,110],[102,103,105,107,108],
    [101,104,106,109,110],[102,105,107,108,110],[101,103,104,107,109],
    [102,104,106,108,110],[101,105,106,107,109],
]

c_lines = []
for i in range(50):
    sid = f"16C{i+1:03d}"
    for cnum in c_pattern[i]:
        cid = f"16C{cnum}"
        s = gen_score()
        c_lines.append(f"('{cid}', '{sid}', '{s}', '16', 'C')")

with open("e:/Grade3/2-DataIntegration/Assignments-DI/As3/docs/hw4/update_bc_scores.sql", "w", encoding="utf-8") as f:
    f.write("-- Re-insert B/C sc data with random scores\n")
    f.write("USE hw4;\n\n")
    f.write("DELETE FROM sc WHERE group_no = '16' AND dept_no IN ('B', 'C');\n\n")
    f.write("-- B: 250 sc records\n")
    f.write("INSERT INTO sc (course_id, student_id, score, group_no, dept_no) VALUES\n")
    f.write(",\n".join(b_lines) + ";\n\n")
    f.write("-- C: 250 sc records\n")
    f.write("INSERT INTO sc (course_id, student_id, score, group_no, dept_no) VALUES\n")
    f.write(",\n".join(c_lines) + ";\n")

# Simulate stats
scores = [gen_score() for _ in range(500)]
print(f"B lines: {len(b_lines)}, C lines: {len(c_lines)}")
print(f"Simulated avg: {sum(scores)/len(scores):.1f}, Min: {min(scores)}, Max: {max(scores)}")
print("Done")
