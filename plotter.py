import matplotlib.pyplot as plt

# Test sizes
x = [100, 500, 1000, 5000, 10000]

# Test results
first = [10.99, 91, 202, 1751.96, 4452.95]
second = [10, 85.04, 205.98, 1707.04, 4541]

# Plot first results
plt.plot(x, first, label='First')

# Plot second results
plt.plot(x, second, label='Second')

# Add labels and title
plt.xlabel('Test Size')
plt.ylabel('Result')
plt.title('Comparison of First and Second Test Results')

# Show a legend
plt.legend()

# Display the plot
plt.show()
