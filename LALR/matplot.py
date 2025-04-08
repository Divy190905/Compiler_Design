"""
Visualization module for LALR parsing tables.

This module provides functions for visualizing ACTION and GOTO tables 
using matplotlib, making them easier to understand.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

def visualize_parsing_tables(action_table, goto_table, terminals, non_terminals, output_file=None):
    """
    Visualize the ACTION and GOTO tables using matplotlib.
    
    Args:
        action_table (dict): The ACTION table mapping (state, symbol) to action
        goto_table (dict): The GOTO table mapping (state, non_terminal) to state
        terminals (list or set): List or set of terminal symbols
        non_terminals (list or set): List or set of non-terminal symbols
        output_file (str, optional): If provided, save the visualization to this file
    """
    # Convert terminals and non_terminals to lists if they are sets
    terminals_list = list(terminals) if isinstance(terminals, set) else terminals
    non_terminals_list = list(non_terminals) if isinstance(non_terminals, set) else non_terminals
    
    # Get all states - handles both nested dict and tuple-key formats
    if action_table and isinstance(next(iter(action_table.keys())), tuple):
        # If keys are tuples like (state, symbol)
        states = sorted(set(state for state, _ in action_table.keys()))
    else:
        # If keys are states and values are dicts
        states = sorted(action_table.keys())
    
    # Create a figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
    fig.suptitle('LALR(1) Parsing Tables', fontsize=16)
    
    # Prepare ACTION table data
    action_data = []
    terminals_with_end = terminals_list + ['$']
    
    for state in states:
        row = []
        for symbol in terminals_with_end:
            # Handle both data structures
            if isinstance(next(iter(action_table.keys())), tuple):
                action = action_table.get((state, symbol), "")
            else:
                # Nested dict structure
                symbol_actions = action_table.get(state, {})
                action = symbol_actions.get(symbol, "")
            row.append(action)
        action_data.append(row)
    
    # Prepare GOTO table data
    goto_data = []
    for state in states:
        row = []
        for symbol in non_terminals_list:
            # Handle both data structures
            if isinstance(next(iter(goto_table.keys())), tuple):
                next_state = goto_table.get((state, symbol), "")
            else:
                # Nested dict structure
                symbol_states = goto_table.get(state, {})
                next_state = symbol_states.get(symbol, "")
            row.append(str(next_state) if next_state != "" else "")
        goto_data.append(row)
    
    # Create custom colormap for different actions
    colors = ['whitesmoke', 'lightgreen', 'lightblue', 'lightsalmon', 'lightyellow']
    cmap = LinearSegmentedColormap.from_list("action_colors", colors, N=5)
    
    # Function to determine cell color based on action
    def get_color_index(action):
        if not action:
            return 0  # Empty cell
        if isinstance(action, str) and action.startswith('s'):
            return 1  # Shift
        if isinstance(action, str) and action.startswith('r'):
            return 2  # Reduce
        if action == 'acc':
            return 3  # Accept
        return 4  # Other/error
    
    # Create color matrices
    action_colors = np.array([[get_color_index(cell) for cell in row] for row in action_data])
    goto_colors = np.zeros((len(states), len(non_terminals_list)))
    for i, row in enumerate(goto_data):
        for j, cell in enumerate(row):
            goto_colors[i, j] = 0 if cell == "" else 4
    
    # Plot ACTION table
    ax1.set_title("ACTION Table")
    ax1.set_ylabel("State")
    ax1.set_yticks(np.arange(len(states)))
    ax1.set_yticklabels(states)
    ax1.set_xticks(np.arange(len(terminals_with_end)))
    ax1.set_xticklabels(terminals_with_end)
    
    # Create ACTION table with color coding
    action_table_plt = ax1.imshow(action_colors, cmap=cmap, aspect='auto')
    
    # Add text to cells
    for i in range(len(states)):
        for j in range(len(terminals_with_end)):
            text = action_data[i][j]
            ax1.text(j, i, text, ha="center", va="center", fontsize=9)
    
    # Plot GOTO table
    ax2.set_title("GOTO Table")
    ax2.set_yticks(np.arange(len(states)))
    ax2.set_yticklabels([])  # Hide y labels as they're shown in ACTION table
    ax2.set_xticks(np.arange(len(non_terminals_list)))
    ax2.set_xticklabels(non_terminals_list)
    
    # Create GOTO table with color coding
    goto_table_plt = ax2.imshow(goto_colors, cmap=cmap, aspect='auto')
    
    # Add text to cells
    for i in range(len(states)):
        for j in range(len(non_terminals_list)):
            text = goto_data[i][j]
            ax2.text(j, i, text, ha="center", va="center", fontsize=9)
    
    # Add legend
    legend_elements = [
        Patch(facecolor=colors[0], edgecolor='gray', label='Empty'),
        Patch(facecolor=colors[1], edgecolor='gray', label='Shift'),
        Patch(facecolor=colors[2], edgecolor='gray', label='Reduce'),
        Patch(facecolor=colors[3], edgecolor='gray', label='Accept'),
        Patch(facecolor=colors[4], edgecolor='gray', label='State')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, bbox_to_anchor=(0.5, 0))
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    # Save to file if output_file is provided
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        return
    
    plt.show()

def visualize_parsing_process(steps, output_file=None):
    """
    Visualize the parsing process as a step-by-step table.
    
    Args:
        steps (list): List of parsing steps
        output_file (str, optional): If provided, save the visualization to this file
    """
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, len(steps) * 0.4 + 2))
    ax.axis('tight')
    ax.axis('off')
    plt.title("Parsing Process Visualization", fontsize=16, pad=20)
    
    # Prepare data for table
    table_data = []
    for i, step in enumerate(steps):
        stack = ' '.join(str(item) for item in step['stack'])
        remaining = ' '.join(str(item) for item in step['input'])
        action = step.get('action', '')
        
        # Format the action with prefix
        if action.startswith('shift'):
            action_formatted = f"s{action.split()[1]}" if len(action.split()) > 1 else "s"
        elif action.startswith('reduce'):
            # Extract production number if available
            parts = action.split()
            if len(parts) > 1:
                action_formatted = f"r{parts[1]}"
            else:
                action_formatted = "r"
        elif action.startswith('accept'):
            action_formatted = "acc"
        elif action == "":
            action_formatted = "start"
        else:
            action_formatted = action
            
        table_data.append([i, stack, remaining, action_formatted])
    
    # Create the table
    table = ax.table(
        cellText=table_data,
        colLabels=['Step', 'Stack', 'Remaining Input', 'Action'],
        cellLoc='center',
        loc='center',
        colWidths=[0.1, 0.4, 0.4, 0.1]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)  # Adjust row height
    
    # Apply colors to different actions
    for i, step in enumerate(steps):
        action = step.get('action', '')
        
        # Apply color based on action type
        if action.startswith('shift'):
            table[(i+1, 3)].set_facecolor('lightgreen')
        elif action.startswith('reduce'):
            table[(i+1, 3)].set_facecolor('lightblue')
        elif action.startswith('accept'):
            table[(i+1, 3)].set_facecolor('lightsalmon')
        
    # Style header row
    for j in range(4):
        table[(0, j)].set_facecolor('lightgray')
    
    # Save to file if output_file is provided
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        return
    
    plt.tight_layout()
    plt.show()