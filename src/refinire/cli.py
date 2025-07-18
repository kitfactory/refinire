#!/usr/bin/env python3
"""
Refinire CLI - Interactive environment variable template generator

This module provides a rich CLI interface for generating environment variable
templates based on user's LLM provider selections.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import oneenv
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    from rich import print as rprint
except ImportError as e:
    print(f"Error: Required dependencies not installed: {e}")
    print("Please install with: pip install 'refinire[cli]'")
    sys.exit(1)

console = Console()

class RefinireTemplateGenerator:
    """Interactive template generator for Refinire environment variables"""
    
    def __init__(self):
        self.console = console
        self.selected_providers: List[Dict[str, str]] = []
        self.selected_features: List[Dict[str, str]] = []
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🚀 Refinire Environment Setup Wizard

Welcome to the Refinire interactive environment variable template generator!

This tool will help you:
- Select LLM providers you want to use
- Choose additional features (tracing, debugging)
- Generate a customized `.env` template file

Let's get started! 🎯
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="[bold cyan]Refinire Setup Wizard[/bold cyan]",
            border_style="cyan"
        ))
        
    def get_available_providers(self) -> List[Tuple[str, str]]:
        """Get available LLM providers from oneenv templates"""
        try:
            # Get LLM category options
            if oneenv.has_category("LLM"):
                options = oneenv.get_options("LLM")
                return [(option, option) for option in options]
            else:
                # Fallback to hardcoded list if oneenv doesn't have the category
                return [
                    ("OpenAI", "OpenAI GPT models"),
                    ("Anthropic", "Claude models"),
                    ("Google", "Gemini models"),
                    ("OpenRouter", "Multiple providers via OpenRouter"),
                    ("Groq", "Fast inference models"),
                    ("Ollama", "Local models"),
                    ("LMStudio", "Local LM Studio models")
                ]
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not get providers from oneenv: {e}[/yellow]")
            return [
                ("OpenAI", "OpenAI GPT models"),
                ("Anthropic", "Claude models"),
                ("Google", "Gemini models"),
                ("OpenRouter", "Multiple providers via OpenRouter"),
                ("Groq", "Fast inference models"),
                ("Ollama", "Local models"),
                ("LMStudio", "Local LM Studio models")
            ]
    
    def select_providers(self) -> List[str]:
        """Interactive LLM provider selection"""
        providers = self.get_available_providers()
        
        # Create provider selection table
        table = Table(title="Available LLM Providers", show_header=True)
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Provider", style="magenta")
        table.add_column("Description", style="white")
        
        for i, (provider, description) in enumerate(providers, 1):
            table.add_row(str(i), provider, description)
        
        self.console.print(table)
        self.console.print()
        
        # Get user selections
        selected_providers = []
        
        while True:
            choice = Prompt.ask(
                "[bold green]Select LLM providers[/bold green] (enter numbers separated by commas, or 'done' to finish)",
                default="1"
            )
            
            if choice.lower() == 'done':
                break
                
            try:
                # Parse comma-separated numbers
                indices = [int(x.strip()) for x in choice.split(',')]
                
                for idx in indices:
                    if 1 <= idx <= len(providers):
                        provider_name = providers[idx - 1][0]
                        if provider_name not in selected_providers:
                            selected_providers.append(provider_name)
                            self.console.print(f"[green]✓[/green] Added {provider_name}")
                    else:
                        self.console.print(f"[red]Invalid selection: {idx}[/red]")
                        
            except ValueError:
                self.console.print("[red]Please enter valid numbers separated by commas[/red]")
        
        if not selected_providers:
            self.console.print("[yellow]No providers selected. Using OpenAI as default.[/yellow]")
            selected_providers = ["OpenAI"]
        
        return selected_providers
    
    def select_features(self) -> List[str]:
        """Select additional features"""
        features = [
            ("Tracing", "OpenTelemetry tracing support"),
            ("Agents", "Agent configuration options"),
            ("Development", "Development and debugging options")
        ]
        
        table = Table(title="Additional Features", show_header=True)
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Feature", style="magenta")
        table.add_column("Description", style="white")
        
        for i, (feature, description) in enumerate(features, 1):
            table.add_row(str(i), feature, description)
        
        self.console.print(table)
        self.console.print()
        
        selected_features = []
        
        for i, (feature, description) in enumerate(features, 1):
            if Confirm.ask(f"Enable {feature}?", default=True):
                selected_features.append(feature)
                self.console.print(f"[green]✓[/green] {feature} enabled")
        
        return selected_features
    
    def generate_template_content(self, providers: List[str], features: List[str]) -> str:
        """Generate template content based on selections"""
        
        # Build selections for oneenv
        selections = []
        
        # Add selected LLM providers
        for provider in providers:
            selections.append({"category": "LLM", "option": provider})
        
        # Add selected features  
        for feature in features:
            if feature == "Tracing":
                selections.append({"category": "Tracing", "option": "OpenTelemetry"})
            elif feature == "Agents":
                selections.append({"category": "Agents", "option": "Configuration"})
            elif feature == "Development":
                selections.append({"category": "Development", "option": "Debugging"})
        
        try:
            # Use oneenv to generate template
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Generating template...", total=None)
                
                # Generate template content
                content = oneenv.generate_template(None, selections)
                
                progress.update(task, description="Template generated!")
                
            return content
            
        except Exception as e:
            self.console.print(f"[red]Error generating template with oneenv: {e}[/red]")
            
            # Fallback to manual template generation
            return self._generate_fallback_template(providers, features)
    
    def _generate_fallback_template(self, providers: List[str], features: List[str]) -> str:
        """Fallback template generation if oneenv fails"""
        lines = [
            "# Refinire Environment Variables",
            "# Generated by Refinire CLI",
            "",
            "# =============================================================================",
            "# LLM Provider Configuration",
            "# =============================================================================",
            ""
        ]
        
        # Add provider-specific variables
        provider_vars = {
            "OpenAI": ["OPENAI_API_KEY="],
            "Anthropic": ["ANTHROPIC_API_KEY="],
            "Google": ["GOOGLE_API_KEY="],
            "OpenRouter": ["OPENROUTER_API_KEY="],
            "Groq": ["GROQ_API_KEY="],
            "Ollama": ["OLLAMA_BASE_URL=http://localhost:11434"],
            "LMStudio": ["LMSTUDIO_BASE_URL=http://localhost:1234/v1"]
        }
        
        for provider in providers:
            if provider in provider_vars:
                lines.append(f"# {provider} Configuration")
                lines.extend(provider_vars[provider])
                lines.append("")
        
        # Add feature-specific variables
        if "Agents" in features:
            lines.extend([
                "# Agent Configuration",
                "REFINIRE_DEFAULT_LLM_MODEL=gpt-4o-mini",
                "REFINIRE_DEFAULT_GENERATION_LLM_MODEL=gpt-4o-mini",
                "REFINIRE_DEFAULT_ROUTING_LLM_MODEL=gpt-4o-mini", 
                "REFINIRE_DEFAULT_EVALUATION_LLM_MODEL=gpt-4o-mini",
                "REFINIRE_DEFAULT_TEMPERATURE=0.7",
                "REFINIRE_DEFAULT_MAX_TOKENS=2048",
                ""
            ])
        
        if "Tracing" in features:
            lines.extend([
                "# OpenTelemetry Tracing",
                "REFINIRE_TRACE_OTLP_ENDPOINT=",
                "REFINIRE_TRACE_SERVICE_NAME=refinire-agent",
                "REFINIRE_TRACE_RESOURCE_ATTRIBUTES=",
                ""
            ])
        
        if "Development" in features:
            lines.extend([
                "# Development & Debugging",
                "REFINIRE_DEBUG=false",
                ""
            ])
        
        return "\n".join(lines)
    
    def save_template(self, content: str, filename: str = ".env.example") -> bool:
        """Save template to file"""
        try:
            output_path = Path(filename)
            
            # Check if file exists
            if output_path.exists():
                if not Confirm.ask(f"File {filename} already exists. Overwrite?"):
                    return False
            
            # Save file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.console.print(f"[green]✅ Template saved to {filename}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error saving template: {e}[/red]")
            return False
    
    def show_summary(self, providers: List[str], features: List[str], filename: str):
        """Show configuration summary"""
        
        summary_text = f"""
## 📋 Configuration Summary

**Selected LLM Providers:**
{chr(10).join(f'• {provider}' for provider in providers)}

**Enabled Features:**
{chr(10).join(f'• {feature}' for feature in features)}

**Output File:** `{filename}`

## 🚀 Next Steps

1. Copy `{filename}` to `.env`
2. Fill in your API keys and configuration values
3. Start using Refinire with your selected providers!

For more information, visit: https://github.com/kitfactory/refinire
        """
        
        self.console.print(Panel(
            Markdown(summary_text),
            title="[bold green]Setup Complete![/bold green]",
            border_style="green"
        ))
    
    def run(self):
        """Run the interactive template generator"""
        try:
            # Welcome
            self.show_welcome()
            
            # Select providers
            self.console.print("[bold magenta]Step 1: Select LLM Providers[/bold magenta]")
            providers = self.select_providers()
            
            # Select features
            self.console.print("\n[bold magenta]Step 2: Select Additional Features[/bold magenta]")
            features = self.select_features()
            
            # Generate template
            self.console.print("\n[bold magenta]Step 3: Generate Template[/bold magenta]")
            content = self.generate_template_content(providers, features)
            
            # Get output filename
            filename = Prompt.ask(
                "[bold green]Output filename[/bold green]",
                default=".env.example"
            )
            
            # Save template
            if self.save_template(content, filename):
                self.show_summary(providers, features, filename)
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Setup cancelled by user.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/red]")


def main():
    """Main entry point for the CLI"""
    generator = RefinireTemplateGenerator()
    generator.run()


if __name__ == "__main__":
    main()