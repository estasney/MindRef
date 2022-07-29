# Decorators

## Simple
```python
def time_it(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        print((datetime.now() - start).total_seconds())
        return result
    return wrapped_func
```

## Keywords
```python
def wait_for(s):
    def dec_wait_for(func):
        @wraps(func)
        def wrapped_wait_for(*args, **kwargs):
            sleep(s)
            return func(*args, **kwargs)
        return wrapped_wait_for
    return dec_wait_for
```
