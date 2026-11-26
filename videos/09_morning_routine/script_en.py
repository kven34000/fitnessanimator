# Morning calisthenics 30 days — English script (estimated timings ~2.7 words/s until the voice is recorded)
_L = [
"Want to change your body? Start with your morning.",                                             # 0
"And no, I don't mean journaling, ice baths or green smoothies.",                                 # 1
"I mean you, the floor, and five minutes of calisthenics.",                                       # 2
"Most people wake up and grab their phone first.",                                                # 3
"Then they wonder why they feel weak, anxious and unfocused.",                                    # 4
"It's simple. Your body isn't moving, so your brain doesn't switch on either.",                   # 5
"Movement first. Focus second.",                                                                  # 6
"This routine is short and simple, and that's exactly why it works.",                             # 7
"It won't burn a thousand calories. It rewires the habit of starting.",                           # 8
"Here's the perfect morning routine. Five exercises, two rounds, five minutes. Let's go.",        # 9
"Push-ups. Thirty seconds, full range.",                                                          # 10
"Can't do them? Use a wall or a bench. Excuses don't count as reps.",                             # 11
"Squats. Thirty seconds. Your legs were built to move, so move them.",                            # 12
"Bird dog. Thirty seconds, opposite arm and leg.",                                                # 13
"You don't need to look cool. You need to stop being weak.",                                      # 14
"Superman hold. Thirty seconds. Lift your arms and legs, and hold.",                              # 15
"If you sit all day, your back is already suffering. Fix it.",                                    # 16
"Plank. Thirty seconds. Want a strong core? Earn it.",                                            # 17
"Rest sixty seconds, then do the whole circuit one more time.",                                   # 18
"Now the most important part.",                                                                   # 19
"Every time you hit snooze for five more minutes, you choose to stay the same.",                  # 20
"This routine breaks that pattern. You start moving, and you start momentum in everything.",      # 21
"Do this for thirty days and you'll get stronger and more mobile.",                               # 22
"But most of all, you'll build real discipline.",                                                 # 23
"Because discipline isn't built when it's easy. It's built in the morning, alone, before the noise.",  # 24
"Anyone can train when they feel like it. Winners train when they don't.",                        # 25
"Still thinking about it? Let me be blunt.",                                                      # 26
"If five minutes is too hard for you, you don't want change. You want comfort.",                  # 27
"That's fine. Just don't lie to yourself.",                                                       # 28
"And if you're ready, you already have the plan. Five minutes, every morning, no exceptions.",    # 29
"Only one question left: will you actually start tomorrow?",                                      # 30
"If yes, write day one in the comments, and subscribe.",                                          # 31
]

SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
