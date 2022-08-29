# pyprojects
Hone your skills in python by doing delicious projects.

Each project is 500 lines of code, give or take.

Intermediate to Advanced projects

1. `ransomware`: Write a simple ransomware. Encrypt and Decrypt files.
2. `virus`: A simple, non-harmful virus written using Python.
3. `caching`: Scroll through Hacker News titles quicky in your terminal and see the difference between using caching or not.
4. `sockets`: Develope a featursome client-server chatroom application using socket programming in Python.

TODO: 
- Explain in each projects which topics are touched upon.
- Run codes through a linter.
- the caching folder, instead of cachetools make use of functools.cache
- Go through the examples once their finished. Very good readme and also maybe packaging them.
- Add testing to some projects. (also CI/CD for the whole repo)
- Add the complete readme's
- In each projects readme add a list of files with the functionality and concepts used.
- For the end project add the tips and tricks (generator expression, mmap file read, ...)
- A Goal section in each readme like: [500lines](https://github.com/aosabook/500lines)
- A tree of files in each project.

QUESTIONS:
1. [DONE] apply a function (e.g. `lambda x: x**2`) to a list in parallel.
2. get input from user at the same time when you are printing something to stdout.
3. functools (caching, ...)
4. concurrent.future (higher level than threading and multiprocessing) -> ThreadPoolExecuter, ProcessPoolExecuter
5. @classmethods, @staticmethod[DONE]
6. special classmethods (__len__ -> len(instance), __next__)[github](https://github.com/CoreyMSchafer/code_snippets/blob/master/Object-Oriented/5-SpecialMethods/oop_test.py)
7. @contexmanager (contextlib) [github](https://github.com/CoreyMSchafer/code_snippets/blob/master/Python-Context-Managers/cm_demo.py)
8. [DONE] sqlite example -> OAuth: [blog](https://robertheaton.com/2019/08/12/programming-projects-for-advanced-beginners-user-logins/)
9. [DONE] sending an email (email lib) as a notification.
10. iterators in python
11. itertools examples (groupby, tee, ...)
12. resources module (memory usage, ...)
13. from multiprocessing import `shared_memory`, share variables across processes. [real python mmap](https://realpython.com/python-mmap/)
14. use `exc_info=True` in logging, `logging.info("some exception occured", exc_info=True)` or use `logging.exception`
15. something with `sqlalchemy`
16. [DONE] dataclasses
17. update some expressions to walrus operator (:=)
