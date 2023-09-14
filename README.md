# Wordle! How lucky is a guess?

Inspired by 3blue1brown

### What is it?

I'm a competitive person; sometimes after comparing my wordle results, I get competitve because while feel I made a better guess, someone else did better with an objectively worse guess. Out of my own competitive spite I started working on this program to calculate just how lucky a guess is, using informational entropy and python. My comments are mostly for me, as this is not ready for public use.

### Progress?

I left off at the optimization stage, my code is slow (very slow) and needs some optimization and maybe a translation into a faster language like c++.

### Did I meet my initial goals?

While I do have a program that works, its massive inefficiency is unsatisfying and I would thus say that I did not me my initial goals (yet)

### What did I learn or gain?

 - I learned about ```map()``` and list comprehensions in python
 - I learned about the ways informational entropy is calculated
 - I learned that empirically proving whether or not someone is lucky is actually a difficult task

### Future plans
 - Optimize the code
 - Clean it up and divide it into a few files
 - Rewrite the bulk functions in c++
 - Make it usable by someone who isn't me: by UI or as a distributed package
