#!/usr/bin/env python3
"""
LR(1) Parsing Table Visualizer

This script generates and visualizes an LR(1) parsing table using Pandas and Matplotlib.
"""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
import numpy as np
import seaborn as sns

# Assuming these are imported from your existing modules
# from grammar import Grammar
# from first_follow import compute_first_sets
# from lr1_items import compute_lr1_automaton
# from parsing_table import construct_parsing_table

def enhance_parsing_table_display(action_table, goto_table, grammar, output_file=None):
    """
    Create a visually appealing display of the parsing table using Pandas and Matplotlib.
    
    Args:
        action_table (dict): The ACTION table mapping (state, terminal) to action
        goto_table (dict): The GOTO table mapping (state, non_terminal) to state
        grammar (Grammar): The grammar object
        output_file (str, optional): If provided, save the visualization to this file
    """
    try:
        # Get the list of states
        states = sorted(set(state for state, _ in action_table.keys()))
        
        # Get the list of terminals and non-terminals
        terminals = sorted(grammar.terminals) + ['$']
        non_terminals = sorted([nt for nt in grammar.non_terminals if nt != grammar.start_symbol])
        
        # Create a DataFrame for ACTION table
        action_data = {}
        for terminal in terminals:
            action_data[terminal] = [format_action(action_table.get((state, terminal), "")) for state in states]
        
        action_df = pd.DataFrame(action_data, index=states)
        action_df.index.name = 'State'
        
        # Create a DataFrame for GOTO table
        goto_data = {}
        for non_terminal in non_terminals:
            goto_data[non_terminal] = [goto_table.get((state, non_terminal), "") for state in states]
        
        goto_df = pd.DataFrame(goto_data, index=states)
        goto_df.index.name = 'State'
        
        # Combine into one table for visualization
        combined_df = pd.concat([action_df, goto_df], axis=1)
        
        # Create a figure with appropriate size
        fig_width = max(12, len(combined_df.columns) * 1.2)
        fig_height = max(8, len(states) * 0.4)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Set up the table styling
        sns.set(font_scale=1.1)
        
        # Create a heatmap with custom coloring
        table = sns.heatmap(combined_df.notna(), cmap=ListedColormap(['white', 'white']),
                            cbar=False, linewidths=1, linecolor='black', ax=ax)
        
        # Add cell text with custom formatting
        for i, col in enumerate(combined_df.columns):
            for j in range(len(states)):
                val = combined_df.iloc[j, i]
                if pd.notna(val) and val != "":
                    # Color coding based on action type
                    if col in terminals:
                        if 's' in str(val):  # Shift
                            color = 'darkblue'
                        elif 'r' in str(val):  # Reduce
                            color = 'darkgreen'
                        elif 'acc' in str(val):  # Accept
                            color = 'darkred'
                        else:
                            color = 'black'
                    else:
                        color = 'purple'  # GOTO actions
                    
                    ax.text(i + 0.5, j + 0.5, val, 
                            horizontalalignment='center', verticalalignment='center',
                            color=color, fontweight='bold')
        
        # Add column divider between ACTION and GOTO tables
        if terminals and non_terminals:
            ax.axvline(x=len(terminals), color='black', linewidth=3)
        
        # Add labels and title
        plt.title("LR(1) Parsing Table", fontsize=16, pad=20)
        
        # Add section labels
        if terminals:
            plt.text(len(terminals)/2, -0.8, "ACTION", horizontalalignment='center', 
                     fontsize=14, fontweight='bold')
        if non_terminals:
            plt.text(len(terminals) + len(non_terminals)/2, -0.8, "GOTO", 
                     horizontalalignment='center', fontsize=14, fontweight='bold')
        
        # Display row and column labels
        ax.set_yticklabels(states, rotation=0)
        ax.set_xticklabels(combined_df.columns, rotation=30, ha="right")
        
        plt.tight_layout()
        
        # Save to file if requested
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Table visualization saved to {output_file}")
        
        # Display the table
        plt.show()
        
        # Print the productions for reference
        print("\nProductions:")
        for i, (lhs, rhs) in enumerate(grammar.productions):
            print(f"{i}: {lhs} -> {' '.join(rhs)}")
            
    except Exception as e:
        print(f"Error generating visualization: {e}")
        print("Make sure matplotlib, pandas and seaborn are installed:")
        print("pip install matplotlib pandas seaborn")

def format_action(action):
    """Format an action for display."""
    if action is None or action == "":
        return ""
    
    if isinstance(action, tuple):
        action_type, value = action
        if action_type == 'shift':
            return f"s{value}"
        elif action_type == 'reduce':
            return f"r{value}"
        elif action_type == 'accept':
            return "acc"
    
    return str(action)

def main():
    """Main function to demonstrate table visualization."""
    # This part would call your existing code to generate the parsing table
    # grammar = get_grammar_input()
    # first_sets = compute_first_sets(grammar)
    # automaton = compute_lr1_automaton(grammar, first_sets)
    # action_table, goto_table, conflicts = construct_parsing_table(automaton, grammar)
    
    # Instead, let's create some sample data for demonstration
    # (You would replace this with your actual parsing table generation)
    
    # Demo code with sample data would go here
    # ...
    
    # Then visualize:
    # enhance_parsing_table_display(action_table, goto_table, grammar, "lr1_table.png")

if __name__ == "__main__":
    main()