"""
OpenTelemetry tracing utilities for Refinire with OpenInference instrumentation.

English: Provides OpenTelemetry tracing capabilities when openinference-instrumentation is available.
日本語: openinference-instrumentationが利用可能な場合にOpenTelemetryトレーシング機能を提供します。
"""

import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    from openinference.instrumentation.openai import OpenAIInstrumentor
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    OPENINFERENCE_AVAILABLE = True
    
    # OTLP exporter is optional
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        OTLP_AVAILABLE = True
    except ImportError:
        OTLP_AVAILABLE = False
        logger.debug("OTLP exporter not available - OTLP export will be disabled")
        
except ImportError as e:
    OPENINFERENCE_AVAILABLE = False
    OTLP_AVAILABLE = False
    logger.debug(f"OpenInference instrumentation not available: {e}. Install with: pip install refinire[openinference-instrumentation]")


class OpenTelemetryTracingProcessor:
    """
    English: Tracing processor that bridges OpenAI Agents SDK spans to OpenTelemetry.
    日本語: OpenAI Agents SDKのスパンをOpenTelemetryに橋渡しするトレーシングプロセッサー。
    """
    
    def __init__(self):
        self._tracer = None
        
    def set_tracer(self, tracer):
        """Set the OpenTelemetry tracer to use for span creation"""
        self._tracer = tracer
    
    def on_trace_start(self, trace):
        """Called when a trace starts"""
        pass
    
    def on_trace_end(self, trace):
        """Called when a trace ends"""
        pass
    
    def on_span_start(self, span):
        """Called when a span starts - create corresponding OpenTelemetry span"""
        if self._tracer is None:
            return
            
        try:
            # Get span data
            span_data = span.span_data
            span_name = getattr(span_data, 'name', 'unknown')
            
            # Create OpenTelemetry span
            otel_span = self._tracer.start_span(span_name)
            
            # Store reference for span_end
            if not hasattr(span, '_otel_span'):
                span._otel_span = otel_span
                
            # Add basic attributes
            if hasattr(span_data, 'input'):
                otel_span.set_attribute("input", str(span_data.input))
            if hasattr(span_data, 'instructions'):
                otel_span.set_attribute("instructions", str(span_data.instructions))
                
        except Exception as e:
            logger.debug(f"Failed to create OpenTelemetry span: {e}")
    
    def on_span_end(self, span):
        """Called when a span ends - finish corresponding OpenTelemetry span"""
        if self._tracer is None:
            return
            
        try:
            # Get the stored OpenTelemetry span
            otel_span = getattr(span, '_otel_span', None)
            if otel_span is None:
                return
                
            # Add end attributes
            span_data = span.span_data
            if hasattr(span_data, 'output'):
                otel_span.set_attribute("output", str(span_data.output))
            if hasattr(span_data, 'success'):
                otel_span.set_attribute("success", bool(span_data.success))
            if hasattr(span_data, 'error'):
                otel_span.set_attribute("error", str(span_data.error))
            if hasattr(span_data, 'model'):
                otel_span.set_attribute("model", str(span_data.model))
            if hasattr(span_data, 'evaluation_score'):
                otel_span.set_attribute("evaluation.score", float(span_data.evaluation_score))
            if hasattr(span_data, 'evaluation_passed'):
                otel_span.set_attribute("evaluation.passed", bool(span_data.evaluation_passed))
                
            # Set status based on success/error
            if hasattr(span_data, 'error') and span_data.error:
                otel_span.set_status(trace.Status(trace.StatusCode.ERROR, str(span_data.error)))
            elif hasattr(span_data, 'success') and span_data.success:
                otel_span.set_status(trace.Status(trace.StatusCode.OK))
                
            # End the span
            otel_span.end()
            
        except Exception as e:
            logger.debug(f"Failed to end OpenTelemetry span: {e}")
    
    def shutdown(self):
        """Shutdown the processor"""
        pass
    
    def force_flush(self):
        """Force flush any pending data"""
        pass


class OpenTelemetryManager:
    """
    English: Manages OpenTelemetry tracing configuration for Refinire agents.
    日本語: RefinireエージェントのOpenTelemetryトレーシング設定を管理します。
    """
    
    def __init__(self):
        self._instrumentor: Optional['OpenAIInstrumentor'] = None
        self._tracer_provider: Optional[TracerProvider] = None
        self._tracing_processor: Optional[OpenTelemetryTracingProcessor] = None
        self._is_enabled = False
    
    def enable_opentelemetry_tracing(
        self,
        service_name: str = "refinire-agent",
        service_version: str = "0.2.10",
        otlp_endpoint: Optional[str] = None,
        console_output: bool = True,
        resource_attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        English: Enable OpenTelemetry tracing with OpenInference instrumentation.
        日本語: OpenInference instrumentationでOpenTelemetryトレーシングを有効化します。
        
        Args:
            service_name: Name of the service for traces
            service_version: Version of the service
            otlp_endpoint: OTLP endpoint URL for trace export (optional, can also use OTEL_EXPORTER_OTLP_ENDPOINT env var)
            console_output: Whether to output traces to console
            resource_attributes: Additional resource attributes for traces
            
        Returns:
            bool: True if successfully enabled, False if openinference not available
            
        Environment Variables:
            REFINIRE_TRACE_OTLP_ENDPOINT: OTLP endpoint URL (e.g., http://192.168.11.15:4317)
            REFINIRE_TRACE_SERVICE_NAME: Service name for traces (overrides service_name parameter)
            REFINIRE_TRACE_RESOURCE_ATTRIBUTES: Additional resource attributes (e.g., "environment=production,team=ai")
        """
        if not OPENINFERENCE_AVAILABLE:
            logger.warning(
                "OpenInference instrumentation not available. "
                "Install with: pip install refinire[openinference-instrumentation]"
            )
            return False
        
        if self._is_enabled:
            logger.info("OpenTelemetry tracing already enabled")
            return True
        
        try:
            # Get configuration from environment variables
            # 環境変数から設定を取得
            env_service_name = os.getenv("REFINIRE_TRACE_SERVICE_NAME", service_name)
            env_otlp_endpoint = os.getenv("REFINIRE_TRACE_OTLP_ENDPOINT", otlp_endpoint)
            env_resource_attrs = os.getenv("REFINIRE_TRACE_RESOURCE_ATTRIBUTES", "")
            
            # Create resource attributes
            default_attributes = {
                "service.name": env_service_name,
                "service.version": service_version,
            }
            
            # Parse environment resource attributes
            # 環境変数のリソース属性をパース
            if env_resource_attrs:
                try:
                    for attr_pair in env_resource_attrs.split(","):
                        if "=" in attr_pair:
                            key, value = attr_pair.strip().split("=", 1)
                            default_attributes[key.strip()] = value.strip()
                except Exception as e:
                    logger.warning(f"Failed to parse REFINIRE_TRACE_RESOURCE_ATTRIBUTES: {e}")
            
            # Override with provided resource attributes
            if resource_attributes:
                default_attributes.update(resource_attributes)
            
            # Set up tracer provider
            resource = Resource.create(default_attributes)
            self._tracer_provider = TracerProvider(resource=resource)
            
            # Add exporters
            processors = []
            
            # Console exporter if requested
            if console_output:
                console_exporter = ConsoleSpanExporter()
                console_processor = BatchSpanProcessor(console_exporter)
                processors.append(console_processor)
            
            # OTLP exporter if endpoint provided and available
            if env_otlp_endpoint and OTLP_AVAILABLE:
                logger.info(f"Configuring OTLP exporter with endpoint: {env_otlp_endpoint}")
                otlp_exporter = OTLPSpanExporter(endpoint=env_otlp_endpoint)
                otlp_processor = BatchSpanProcessor(otlp_exporter)
                processors.append(otlp_processor)
            elif env_otlp_endpoint and not OTLP_AVAILABLE:
                logger.warning("OTLP endpoint provided but OTLP exporter not available. Install with: pip install opentelemetry-exporter-otlp")
            elif env_otlp_endpoint is None:
                logger.info("No OTLP endpoint configured. Set REFINIRE_TRACE_OTLP_ENDPOINT to enable OTLP export.")
            
            # Add processors to tracer provider
            for processor in processors:
                self._tracer_provider.add_span_processor(processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self._tracer_provider)
            
            # Instrument OpenAI
            self._instrumentor = OpenAIInstrumentor()
            self._instrumentor.instrument()
            
            # Set up tracing processor to bridge Agents SDK spans to OpenTelemetry
            self._tracing_processor = OpenTelemetryTracingProcessor()
            tracer = trace.get_tracer("refinire-agent")
            self._tracing_processor.set_tracer(tracer)
            
            # Register the tracing processor with Agents SDK
            try:
                from agents.tracing import add_trace_processor
                add_trace_processor(self._tracing_processor)
            except ImportError:
                logger.debug("Could not register tracing processor - agents.tracing not available")
            
            self._is_enabled = True
            logger.info(f"OpenTelemetry tracing enabled for service: {env_service_name}")
            if env_otlp_endpoint:
                logger.info(f"Traces will be sent to: {env_otlp_endpoint}")
            if console_output:
                logger.info("Console tracing output enabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable OpenTelemetry tracing: {e}")
            return False
    
    def disable_opentelemetry_tracing(self) -> None:
        """
        English: Disable OpenTelemetry tracing and clean up resources.
        日本語: OpenTelemetryトレーシングを無効化してリソースをクリーンアップします。
        """
        if not self._is_enabled:
            return
        
        try:
            if self._instrumentor:
                self._instrumentor.uninstrument()
                self._instrumentor = None
            
            if self._tracer_provider:
                self._tracer_provider.shutdown()
                self._tracer_provider = None
            
            self._is_enabled = False
            logger.info("OpenTelemetry tracing disabled")
            
        except Exception as e:
            logger.error(f"Error disabling OpenTelemetry tracing: {e}")
    
    def is_enabled(self) -> bool:
        """
        English: Check if OpenTelemetry tracing is currently enabled.
        日本語: OpenTelemetryトレーシングが現在有効かどうかを確認します。
        
        Returns:
            bool: True if tracing is enabled
        """
        return self._is_enabled
    
    def get_tracer(self, name: str = "refinire"):
        """
        English: Get a tracer instance for manual span creation.
        日本語: 手動スパン作成用のトレーサーインスタンスを取得します。
        
        Args:
            name: Name of the tracer
            
        Returns:
            Tracer instance if available, None otherwise
        """
        if not self._is_enabled or not OPENINFERENCE_AVAILABLE:
            return None
        
        return trace.get_tracer(name)


# Global instance
_opentelemetry_manager = OpenTelemetryManager()


def enable_opentelemetry_tracing(
    service_name: str = "refinire-agent",
    service_version: str = "0.2.10",
    otlp_endpoint: Optional[str] = None,
    console_output: bool = True,
    resource_attributes: Optional[Dict[str, Any]] = None
) -> bool:
    """
    English: Enable OpenTelemetry tracing with OpenInference instrumentation.
    日本語: OpenInference instrumentationでOpenTelemetryトレーシングを有効化します。
    
    Args:
        service_name: Name of the service for traces (can be overridden by OTEL_SERVICE_NAME env var)
        service_version: Version of the service
        otlp_endpoint: OTLP endpoint URL for trace export (can be overridden by OTEL_EXPORTER_OTLP_ENDPOINT env var)
        console_output: Whether to output traces to console
        resource_attributes: Additional resource attributes for traces
        
    Returns:
        bool: True if successfully enabled, False if openinference not available
        
    Environment Variables:
        REFINIRE_TRACE_OTLP_ENDPOINT: OTLP endpoint URL (e.g., http://192.168.11.15:4317)
        REFINIRE_TRACE_SERVICE_NAME: Service name for traces
        REFINIRE_TRACE_RESOURCE_ATTRIBUTES: Additional resource attributes (e.g., "environment=production,team=ai")
        
    Examples:
        # Enable with console output only
        enable_opentelemetry_tracing()
        
        # Enable with OTLP export to Grafana Tempo
        enable_opentelemetry_tracing(
            service_name="my-agent",
            otlp_endpoint="http://192.168.11.15:4317",
            resource_attributes={"environment": "production"}
        )
        
        # Or use environment variables
        # export REFINIRE_TRACE_OTLP_ENDPOINT=http://192.168.11.15:4317
        # export REFINIRE_TRACE_SERVICE_NAME=my-agent
        # export REFINIRE_TRACE_RESOURCE_ATTRIBUTES=environment=production,team=ai
        enable_opentelemetry_tracing()
    """
    return _opentelemetry_manager.enable_opentelemetry_tracing(
        service_name=service_name,
        service_version=service_version,
        otlp_endpoint=otlp_endpoint,
        console_output=console_output,
        resource_attributes=resource_attributes
    )


def disable_opentelemetry_tracing() -> None:
    """
    English: Disable OpenTelemetry tracing and clean up resources.
    日本語: OpenTelemetryトレーシングを無効化してリソースをクリーンアップします。
    """
    _opentelemetry_manager.disable_opentelemetry_tracing()


def is_opentelemetry_enabled() -> bool:
    """
    English: Check if OpenTelemetry tracing is currently enabled.
    日本語: OpenTelemetryトレーシングが現在有効かどうかを確認します。
    
    Returns:
        bool: True if tracing is enabled
    """
    return _opentelemetry_manager.is_enabled()


def is_openinference_available() -> bool:
    """
    English: Check if OpenInference instrumentation is available.
    日本語: OpenInference instrumentationが利用可能かどうかを確認します。
    
    Returns:
        bool: True if openinference-instrumentation is installed
    """
    return OPENINFERENCE_AVAILABLE


def get_tracer(name: str = "refinire"):
    """
    English: Get a tracer instance for manual span creation.
    日本語: 手動スパン作成用のトレーサーインスタンスを取得します。
    
    Args:
        name: Name of the tracer
        
    Returns:
        Tracer instance if available, None otherwise
    """
    return _opentelemetry_manager.get_tracer(name)