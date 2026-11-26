# The most boring exercise that fixes everything (dead hang) — English script (~2.7 words/s estimate)
_L = [
# A hook (0-4)
"Find a bar. Grab it. Lift your feet. That's it.",                                               # 0
"No reps, no weight, nothing moves. It's the most boring exercise in the gym.",                  # 1
"Last week I tried it. Nine seconds, and my hands gave out. Nine seconds, for a guy who trains six days a week.",  # 2
"But this boring exercise does three things most workouts never touch: your shoulders, your spine, and your grip.",  # 3
"And for grip, there's a study of almost a hundred and forty thousand people, with one number that beat blood pressure. Stay till the end.",  # 4
# B overhead (5-8)
"As a kid, you hung from bars just for fun. When did your hands last hold your whole body weight overhead?",  # 5
"For most people, years ago. Everything we train is in front of us: bench press, push-ups, phone, keyboard.",  # 6
"We push things away, or pull them in low. But overhead? Empty.",                                # 7
"Strange, because our ancestors had shoulders built a lot like a chimp's. We're made to hang. We just stopped.",  # 8
# C surgery (9-16)
"And when shoulders start to hurt, the standard answer for years was surgery: shave bone off the top of the shoulder to make room for the tendon.",  # 9
"Then doctors in Britain did something bold. They tested that surgery against a fake one.",      # 10
"In the fake one, the surgeon opened the shoulder, looked inside, and removed nothing. Patients didn't know which one they got.",  # 11
"Six months later: no difference. The real surgery worked no better than the fake.",             # 12
"A team in Finland followed their patients for ten years. Same story.",                          # 13
"So if cutting bone doesn't create space, what does?",                                           # 14
"Scientists put people in an MRI with one arm raised. When they pulled the arm down against resistance, the gap above the tendon got bigger.",  # 15
"In some positions, twice as big as when they pushed up. That's level two of the hang. We'll get there.",  # 16
# D basic hang (17-21)
"But first, the basic hang. Grab the bar slightly wider than your shoulders, thumbs wrapped around.",  # 17
"Arms straight. Feet off the ground. Body long and still. Breathe.",                             # 18
"You should feel a stretch in your armpits, your lats and your forearms.",                       # 19
"Don't swing or kick your legs. A hang is silence. The body stays straight.",                    # 20
"At first, your seconds will be small. Nine, then twelve, then fifteen. That's normal. Write it down every time.",  # 21
# E spine (22-27)
"All day long, your spine gets compressed: sitting, standing, carrying. That's why you're a few millimeters shorter in the evening.",  # 22
"When you hang, everything flips. Your legs stop pressing on your spine and start pulling it down.",  # 23
"In studies, twenty minutes of traction made people a few millimeters taller. But half an hour after standing up, it was gone.",  # 24
"So hanging won't rebuild your back. It's a pause. A good pause between hours in the chair.",     # 25
"Real disc recovery happens at night, when you lie down and the discs soak water back up.",      # 26
"So in a passive hang, let your legs go heavy, relax your face, and breathe out slowly. Gravity does the work.",  # 27
# F grip (28-34)
"Back to my nine seconds. My shoulders didn't quit. My hands did. In a hang, grip goes first.",   # 28
"And this is where grip gets serious. Researchers followed almost a hundred and forty thousand adults in seventeen countries for four years.",  # 29
"They measured one simple thing: how hard each person could squeeze.",                           # 30
"For every five kilos of lost grip strength, the risk of dying in those four years went up by sixteen percent.",  # 31
"And grip predicted it better than blood pressure.",                                             # 32
"Careful: weak grip doesn't kill you. Strong hands usually come with a body that still gets used. Grip is a warning light, not the engine.",  # 33
"A later review of more than three million people found the same sixteen percent.",              # 34
# G levels (35-42)
"Now the boredom problem. When an exercise gets easy, it stops working.",                        # 35
"Climbers tested this. One group hung for time. The other did the same, but added a little weight every week.",  # 36
"After eight weeks, only the group that added weight had a stronger grip. That's why the hang has levels.",  # 37
"Level one: the passive hang you just learned. Relaxed, long, quiet. Once you can hold sixty seconds, move up.",  # 38
"Level two: the active hang. Pull your shoulder blades down, away from your ears, without bending your elbows. Your body rises a couple of centimeters. Hold it.",  # 39
"That's the very start of a pull-up, and close to the movement that opened the gap in the MRI. Only the shoulder blades move.",  # 40
"Level three: the leg raise hang. From the active hang, lift both legs straight out to hip height. Grip, shoulders and abs all work at once.",  # 41
"Straight legs too hard? Pull your knees to your chest first.",                                  # 42
# H numbers & plan (43-53)
"How long is good? In one study, active young men hung about seventy-three seconds. Trained motocross riders hung about a hundred and thirteen.",  # 43
"Your grip adapts to the work you give it. Some coaches say: aim for two minutes. Not science, but a good goal.",  # 44
"The plan: a doorway bar, or any bar at the gym. Three days a week, at the start of your workout.",  # 45
"Three hangs at your level, as long as you can with clean form. One minute of rest between them.",  # 46
"Can't hang for ten seconds? Put a box under the bar, keep your toes on it, and let your hands take most of the weight.",  # 47
"When you finish, never just let go and drop. Feet down first, then release.",                   # 48
"Log your best hang every time. Passive up to sixty seconds, then active, then legs.",           # 49
"And when the leg raise hang gets easy, hold a light dumbbell between your feet.",               # 50
"In one climbing study, adding about a kilo and a half every week built grip better than climbing itself.",  # 51
"I started at nine seconds. Five weeks later: fifty-two seconds, and not a single swing.",        # 52
"Still the most boring exercise in the gym. And that's exactly why nobody else does it.",        # 53
]

SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
