# Walking vs belly fat — English script (estimated timings ~2.7 words/s until the voice is recorded)
_L = [
# A hook (0-8)
"This cookie has six hundred calories.",                                              # 0
"To burn it off, you'd have to sprint for fifty-five minutes.",                         # 1
"Fifty-five minutes of sweat, gasping and pain. For one snack.",                        # 2
"You can't outrun your fork.",                                                          # 3
"But you can outsmart your metabolism.",                                                # 4
"Most people think fitness is a pain contest.",                                         # 5
"They sprint, do HIIT, suffer, and look exactly the same six months later.",            # 6
"Today I'll show you a walking protocol that doesn't just burn calories. It hacks your insulin.",  # 7
"Give me six minutes, and I'll save you ten years of useless cardio.",                  # 8
# B stubborn belly (9-17)
"You diet for weeks. Your face gets leaner. Your arms get leaner.",                     # 9
"But the belt around your waist doesn't move.",                                         # 10
"That's not laziness. It's a defense system.",                                          # 11
"Back in the nineties, researchers found that fat cells have switches.",                # 12
"Beta receptors are a green light. Adrenaline hits them, the cell opens, and the energy burns.",  # 13
"Your face, arms and chest are full of them. That's why they lean out first.",          # 14
"Alpha receptors are a red light. The cell locks its doors and holds on to the fat.",   # 15
"And belly fat has far more of these red lights than the rest of your body.",           # 16
"Evolution put them there to protect your organs from starvation.",                     # 17
# C cardio trap (18-22)
"Here's the trap. Sprints, CrossFit, brutal intervals.",                                # 18
"They flood your body with stress hormones: adrenaline and cortisol.",                  # 19
"In your arms, adrenaline hits the green light. In your belly, it hits the red one.",   # 20
"And chronically high cortisol is directly linked to belly fat storage.",               # 21
"You're literally working harder to stay fatter.",                                      # 22
# D two fuel tanks (23-31)
"Picture two fuel tanks.",                                                              # 23
"Tank A is small and high octane. That's sugar, for sprinting and heavy lifting.",      # 24
"Tank B is a giant tanker. That's your body fat, for slow, long, easy work.",           # 25
"A big review of fifty-four studies found the same thing.",                             # 26
"High intensity burns mostly sugar. Low intensity burns mostly fat.",                   # 27
"When you run, you burn your lunch. When you walk, you burn your belly.",               # 28
"While walking you can still talk. That's zone two. Cortisol stays low, and the red lights stay quiet.",  # 29
"So the answer is walking.",                                                            # 30
"But strolling around the couch won't give you abs. Or every mailman would be shredded.",  # 31
# E calorie myth (32-39)
"On paper, running wins: about three fifty calories in thirty minutes, versus one fifty for walking.",  # 32
"But you're not a spreadsheet. Hard training spikes ghrelin, your hunger hormone.",     # 33
"An hour later you're starving. Extra bread with butter: four hundred calories.",       # 34
"Congratulations. You suffered thirty minutes to end up plus fifty.",                   # 35
"And you're wiped out. Couch, elevator, less moving all day.",                          # 36
"Walking doesn't spike your hunger and doesn't drain you.",                             # 37
"One hour a day is three hundred calories. That's twenty-one hundred a week, and about fourteen kilos of fat a year.",  # 38
"The runner quits in three weeks with sore knees. The walker wins, because he never stops.",  # 39
# F step 1 (40-45)
"Here's the protocol. Insulin is a storage hormone. While it's high, fat burning is switched off.",  # 40
"Step one: the after-meal walk.",                                                       # 41
"Research shows a ten minute walk right after eating controls blood sugar far better than walking at any other time.",  # 42
"Your rule: three ten minute walks a day. After breakfast, after lunch, after dinner.", # 43
"That's thirty minutes of cardio and three thousand steps, without changing into gym clothes.",  # 44
"Your muscles burn the meal as fuel instead of storing it on your belly.",              # 45
# G step 2 NEAT (46-50)
"Step two: NEAT. The calories you burn just by living. It can differ by two thousand a day between lean and heavy people.",  # 46
"Hack one: park at the far end. Plus four hundred steps.",                              # 47
"Hack two: never sit on a phone call. Walk around.",                                    # 48
"Hack three: kill the elevator. Stairs burn three times more.",                         # 49
"Do all that and you'll hit eight to ten thousand steps almost by accident.",           # 50
# H step 3 incline (51-55)
"Step three, for the impatient: incline walking. The nuclear option.",                  # 51
"It doubles the workload without the impact of running. Your glutes and hamstrings work at maximum.",  # 52
"The viral twelve three thirty: incline twelve, speed three, thirty minutes.",          # 53
"One rule: don't hold the rails. Grab them, and incline twelve becomes incline two.",   # 54
"Can't do it hands free? Drop to eight. Two or three sessions a week.",                 # 55
# I nutrition (56-59)
"But if you eat like a trash can, none of this works.",                                 # 56
"Remember the cookie: an hour of walking to burn it, forty-five seconds to eat it.",    # 57
"Food is the engine. Walking is the turbo. No fuel in the tank, and the car goes nowhere.",  # 58
"A small daily deficit, plus this protocol, and the fat has nowhere left to hide.",     # 59
# J plan + challenge (60-65)
"Weeks one to four: check your average steps, add two thousand, and walk after every meal.",  # 60
"Weeks five to eight: at least eight thousand steps a day. Rain or snow. Add the hacks.",  # 61
"Weeks nine to twelve: ten to twelve thousand steps, plus two incline sessions.",       # 62
"Walking is the oldest movement we have. It clears your head, saves your joints, and burns belly fat.",  # 63
"My challenge: seven days. Track your steps, and walk ten minutes after every meal.",   # 64
"Come back in a week. More energy, less bloating, and looser pants.",                   # 65
]
SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
