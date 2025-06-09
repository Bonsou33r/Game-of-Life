**Save to subdirectory:**
```python
np.save('grids/my_pattern.npy', grid_array)
```

**Load from subdirectory:**
```python
grid = np.load('grids/my_pattern.npy')
```

You can also use `os.path.join()` for cross-platform compatibility:
```python
import os
path = os.path.join('grids', 'my_pattern.npy')
np.save(path, grid_array)
```

Just make sure the directory exists first - Python won't create it automatically. Use `os.makedirs('grids', exist_ok=True)` to create it if needed.


