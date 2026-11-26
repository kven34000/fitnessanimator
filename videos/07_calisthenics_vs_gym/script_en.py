# Calisthenics or gym — English script (~2.7 words/s estimate)
_L = [
# A hook (0-3)
"So you finally decided to start training. Great choice. But now comes the big question: calisthenics, or the gym?",  # 0
"Option one: muscle-ups on a rusty bar in the park, while a dog barks at you.",                  # 1
"Option two: waiting twenty minutes for a bench, because someone is sitting on it filming a TikTok.",  # 2
"Both can work. But which one is right for you? Let's break it down.",                           # 3
# B what (4-11)
"Calisthenics is raw, natural training. Your body is your machine.",                             # 4
"No dumbbells, no machines, no special equipment. Just you and gravity.",                        # 5
"You push, pull and move your body as one unit: arms, legs and core all working together.",      # 6
"You start with the basics: push-ups, pull-ups, squats and dips.",                               # 7
"And at higher levels, you unlock skills like the planche, the front lever and the muscle-up.",  # 8
"Now the other side. The gym is dumbbells, barbells, cables and machines.",                      # 9
"You build your body like a project. Add a few kilos today, a few more next week, and you see progress in real time.",  # 10
"Both build strength and muscle. But the final look, and the path there, are different.",        # 11
# C money (12-17)
"Money. Before we talk results, let's talk about the thing that breaks most people.",            # 12
"Calisthenics is basically free. No membership, no monthly fees. Gravity doesn't charge you.",   # 13
"Train at home, in a park, or even in a doorway. Bands, a pull-up bar or rings are nice upgrades, but optional. The basics are always free.",  # 14
"The gym costs money. A budget membership is about forty dollars a month, and a fancy one with a sauna is closer to a hundred.",  # 15
"A home gym isn't cheap either. Barbell, plates, rack, and you've spent a thousand dollars before your first rep.",  # 16
"On cost, calisthenics wins easily.",                                                            # 17
# D ease (18-24)
"How easy is it to start? On paper, calisthenics looks simple. Push-ups, pull-ups, dips.",        # 18
"In reality, most beginners can do a few push-ups and not a single pull-up.",                    # 19
"From day one, you lift your whole body weight, whether you weigh fifty kilos or a hundred. There's no easy mode.",  # 20
"So progress starts slow. Your first pull-up can take weeks, or months.",                        # 21
"In the gym it's easier. Dumbbells start at two kilos, cables let you pick a tiny weight, and many machines guide the movement for you.",  # 22
"A beginner can sit at the lat pulldown, pick a light weight, and build strength long before their first pull-up.",  # 23
"For beginners, the gym is the easier way in.",                                                  # 24
# E strength type (25-29)
"Different strength. Calisthenics builds functional strength: core on, balance steady, every movement connected. You feel like an athlete.",  # 25
"The gym is the best way to add muscle mass. Barbells give you loads you can't get with bodyweight, especially for legs.",  # 26
"A pistol squat can't compete with a heavy barbell squat.",                                      # 27
"And in the gym you can isolate any muscle: biceps, hamstrings, shoulders, anything.",            # 28
"Want body control and athleticism? Calisthenics. Want maximum size and symmetry? The gym.",     # 29
# F progress (30-33)
"Progress. In the gym it's simple: five reps with thirty kilos today, thirty-two next week. Clear, measurable, easy to track.",  # 30
"In calisthenics, progress means new levels: push-ups, then archer push-ups, then one-arm push-ups. Pull-ups, then muscle-ups, then the front lever.",  # 31
"Each step can take months, and it's harder to measure.",                                        # 32
"Want fast, clear growth? The gym. Love the path of skills? Calisthenics.",                      # 33
# G fat loss (34-37)
"Fat loss. Most people start training to lose weight. But neither one burns fat by itself. Nutrition plus cardio does.",  # 34
"If you're overweight, calisthenics can be brutal. Push-ups and pull-ups with extra weight are torture.",  # 35
"In the gym, you can pick a light weight and train safely. Plus there are treadmills, bikes and ellipticals.",  # 36
"If fat loss is the goal, the gym is usually easier.",                                           # 37
# H environment (38-40)
"Environment and motivation. Calisthenics is freedom: train anywhere. But the motivation is all on you.",  # 38
"The gym is atmosphere: clanging iron, music, people around you. Even if you talk to no one, the place makes you work.",  # 39
"But the commute, or a bad mood, easily turns into an excuse.",                                  # 40
# I safety + final (41-45)
"Safety. Both are safe with good form. Bad technique, ego lifting and bad programs cause injuries, not the method.",  # 41
"And no, lifting weights doesn't stunt a teenager's growth. That's a myth.",                     # 42
"Bottom line: both give you strength, health and results. And you don't have to pick just one.", # 43
"Combine them: skills and control from calisthenics, plus strength and size from the gym.",      # 44
"So which side are you on? Calisthenics, or the gym? Tell me in the comments.",                  # 45
]

SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
