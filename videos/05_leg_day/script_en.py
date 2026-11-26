# Why leg day changes everything — English script (estimated timings ~2.7 words/s until the voice is recorded)
_L = [
# A hook (0-6)
"You can do pull-ups, train abs, and have shredded arms.",                                       # 0
"But if you skip leg day, you don't look like an athlete. You look like a Wi-Fi signal: strong on top, weak at the bottom.",  # 1
"Most people avoid leg day because it's hard, boring, or nobody looks down there anyway.",       # 2
"And that's exactly why their body looks unfinished.",                                           # 3
"Your legs aren't just support. They're the foundation of your strength, balance, endurance, and even how your upper body looks.",  # 4
"Legs are the biggest muscle group in your body: quads, hamstrings, glutes and calves.",         # 5
"When they work, your whole body wakes up.",                                                     # 6
# B why (7-14)
"Hormones. Every heavy squat tells your brain: we need more testosterone and more growth hormone.",  # 7
"Those are what make you stronger, leaner and more energetic.",                                  # 8
"Metabolism. After a hard leg day, your body stays revved up for up to twenty-four hours.",      # 9
"You can lie on the couch and still keep burning calories. It's bonus cardio that happens by itself.",  # 10
"Endurance and power. Strong legs mean climbing stairs without getting tired, running, and full control of your body.",  # 11
"Proportions. Legs make your body look athletic and complete. Big shoulders on skinny legs just look unbalanced.",  # 12
"And don't try to replace leg day with running or cycling. It's not the same.",                  # 13
"Cardio won't build real strength in your quads and glutes. Without resistance, muscles don't grow.",  # 14
# C warm-up (15-18)
"Warm-up isn't a waste of time. Cold muscles are slow, weak and easy to injure. Warm muscles are fast, strong and responsive.",  # 15
"Three to four minutes is enough. Thirty seconds of jumping jacks to raise your temperature.",   # 16
"Ten easy bodyweight squats. Ten lunges to wake up your balance. Done.",                         # 17
"It's a warm-up for your head too: put the phone away and switch into training mode.",           # 18
# D exercises (19-29)
"Strong legs don't need a hundred exercises. Just one move for each zone, with a home and a gym version.",  # 19
"Quads. Bodyweight squat: feet a bit wider than shoulders, toes slightly out, chest up.",         # 20
"More than thirty easy reps? Add weight: a backpack, a dumbbell, or water bottles.",              # 21
"In the gym: the barbell squat. Bar on your traps, neutral spine, down to parallel. The last one or two reps should be hard, but clean.",  # 22
"Hamstrings. Bodyweight good morning: hands behind your head, hinge from the hips, back flat. Two seconds down, one up.",  # 23
"In the gym: the Romanian deadlift. Soft knees, bar close to your legs. Control beats weight.",   # 24
"Glutes. The glute bridge. At the top, knees, hips and shoulders form one line. Pause for one second.",  # 25
"Make it harder with your feet raised, or one leg at a time.",                                   # 26
"Calves. Standing calf raises. Full range, pause at the top, slow on the way down.",              # 27
"Too easy? Add a backpack, or go one leg at a time.",                                            # 28
"The rule for all of them: it's not about speed, and it's not about weight. It's about control.",  # 29
# E frequency (30-33)
"The biggest mistake is training legs once a month and expecting growth.",                       # 30
"Beginner? Once a week is enough. Pick a fixed day, like Saturday. Skip it, and you push your progress back a week.",  # 31
"Training regularly? Add a second day: Monday heavy, Thursday light, for technique and endurance.",  # 32
"Legs are big, and they need recovery. Smash them every day and you don't grow. You just burn out.",  # 33
# F recovery (34-39)
"Train, eat, sleep, recover, repeat. That's the growth formula.",                                # 34
"Never skip sleep. Seven to eight hours minimum. That's when growth hormone is released and your muscles rebuild.",  # 35
"No food, no growth. Protein builds muscle, carbs give energy, fats support your hormones.",      # 36
"Aim for at least one point six grams of protein per kilo of bodyweight.",                       # 37
"Progress isn't big jumps. One more rep, two and a half more kilos, a bit less rest. Your body loves small steps.",  # 38
"Control the lowering phase, it's work too. And after training, five minutes of stretching.",    # 39
# G final (40-43)
"Building legs is slow. But they're the foundation, and a foundation takes time and lasts a lifetime.",  # 40
"Sleep, eat, control every rep, and repeat. You won't just build legs. You'll build a body that moves with real strength.",  # 41
"Train your chest and arms all you want. Without strong legs, you're not an athlete.",           # 42
"If this helped, hit like, subscribe, and tell me in the comments how often you really train legs.",  # 43
]

SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
