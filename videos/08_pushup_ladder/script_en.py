# 80+ push-ups (ladder method) — English script (estimated timings ~2.7 words/s until the voice is recorded)
_L = [
"Here's how to go from ten push-ups to a hundred, with one method almost nobody talks about.",   # 0
"You can do hundreds of push-ups every day and still see zero progress.",                         # 1
"But after this video, you'll come back and say: thanks, this actually works.",                   # 2
"Now the honest part. Ninety-nine percent of people quit after three or four days.",              # 3
"But whoever doesn't quit will see progress they've never had before.",                           # 4
"And the best part? It's simple.",                                                                # 5
"First, stop training like everyone else.",                                                       # 6
"Five sets of fifteen will never get you to fifty in a row.",                                     # 7
"Instead, do fewer sets, but take every set to true failure, when you physically can't do one more rep.",  # 8
"Use this principle, and in two months you can hit fifty-plus push-ups in a single set.",         # 9
"The secret is called the ladder method.",                                                        # 10
"Start with the hardest version you can do. For example, decline push-ups with your feet up on a box. Go to failure.",  # 11
"Then immediately drop to regular push-ups. Failure again.",                                      # 12
"Then incline push-ups, hands on a bench. To failure.",                                           # 13
"And finish with knee push-ups. To failure.",                                                     # 14
"Do this ladder two or three times a day, three or four days a week.",                            # 15
"In a few weeks you'll feel the difference. Progress comes from good form and consistency.",      # 16
"And if you keep switching workouts and never know what works, make a simple plan.",              # 17
"Push-ups, pulls, squats and holds. Follow it for at least one month.",                           # 18
"That's enough to see real progress, and to move toward skills like the handstand, the L-sit and the front lever.",  # 19
"So don't wait for the perfect moment. Start today, and tell me in the comments how many push-ups you can do right now.",  # 20
]

SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
