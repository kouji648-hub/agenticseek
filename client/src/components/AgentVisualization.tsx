import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Loader2, XCircle, Play, RefreshCw, Brain, Search, Code, Globe, ClipboardList, Lightbulb } from "lucide-react";

interface AgentThought {
  id: string;
  content: string;
  thought_type: "planning" | "analysis" | "decision" | "observation";
  timestamp: string;
}

interface AgentAction {
  id: string;
  action_type: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at?: string;
  completed_at?: string;
  result?: string;
  error?: string;
}

interface AgentExecution {
  execution_id: string;
  task: string;
  status: "pending" | "running" | "completed" | "failed";
  thoughts: AgentThought[];
  actions: AgentAction[];
  logs: string[];
  current_action: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  final_result?: string;
}

interface AgentVisualizationProps {
  apiBaseUrl?: string;
}

export default function AgentVisualization({ apiBaseUrl = "http://localhost:7777" }: AgentVisualizationProps) {
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<AgentExecution | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch all executions
  const fetchExecutions = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/agent/executions`);
      const data = await response.json();
      setExecutions(data.executions || []);

      // Update selected execution if exists
      if (selectedExecution) {
        const updated = data.executions.find((e: AgentExecution) => e.execution_id === selectedExecution.execution_id);
        if (updated) {
          setSelectedExecution(updated);
        }
      }
    } catch (error) {
      console.error("Failed to fetch executions:", error);
    }
  };

  // Start demo execution
  const startDemoExecution = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/agent/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: "Demo AI Agent Task" }),
      });
      const data = await response.json();

      // Wait a moment then fetch executions to get the new execution
      setTimeout(() => {
        fetchExecutions();
      }, 500);
    } catch (error) {
      console.error("Failed to start demo execution:", error);
    } finally {
      setLoading(false);
    }
  };

  // Delete execution
  const deleteExecution = async (executionId: string) => {
    try {
      await fetch(`${apiBaseUrl}/agent/execution/${executionId}`, {
        method: "DELETE",
      });
      fetchExecutions();
      if (selectedExecution?.execution_id === executionId) {
        setSelectedExecution(null);
      }
    } catch (error) {
      console.error("Failed to delete execution:", error);
    }
  };

  // Auto-refresh when an execution is running
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      const hasRunning = executions.some((e) => e.status === "running");
      if (hasRunning || selectedExecution?.status === "running") {
        fetchExecutions();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, executions, selectedExecution]);

  // Initial fetch
  useEffect(() => {
    fetchExecutions();
  }, []);

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "running":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  // Get status badge variant
  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case "completed":
        return "default";
      case "failed":
        return "destructive";
      case "running":
        return "secondary";
      default:
        return "outline";
    }
  };

  // Get action icon
  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "search":
        return <Search className="w-4 h-4" />;
      case "browse":
        return <Globe className="w-4 h-4" />;
      case "code":
        return <Code className="w-4 h-4" />;
      case "analyze":
        return <Brain className="w-4 h-4" />;
      case "plan":
        return <ClipboardList className="w-4 h-4" />;
      default:
        return <Circle className="w-4 h-4" />;
    }
  };

  // Get thought icon
  const getThoughtIcon = (thoughtType: string) => {
    switch (thoughtType) {
      case "planning":
        return <ClipboardList className="w-4 h-4 text-blue-500" />;
      case "analysis":
        return <Brain className="w-4 h-4 text-purple-500" />;
      case "decision":
        return <Lightbulb className="w-4 h-4 text-yellow-500" />;
      case "observation":
        return <Search className="w-4 h-4 text-green-500" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">AI Agent Execution</h2>
          <p className="text-sm text-slate-400">Monitor agent thoughts and actions in real-time</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className="bg-slate-700 border-slate-600 text-white hover:bg-slate-600"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? "animate-spin" : ""}`} />
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
          </Button>
          <Button onClick={startDemoExecution} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
            <Play className="w-4 h-4 mr-2" />
            {loading ? "Starting..." : "Start Demo Agent"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Execution List */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">All Executions</CardTitle>
            <CardDescription className="text-slate-400">
              {executions.length} execution{executions.length !== 1 ? "s" : ""} tracked
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {executions.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <p>No executions yet</p>
                  <p className="text-sm mt-2">Click "Start Demo Agent" to see agent execution</p>
                </div>
              ) : (
                executions.map((execution) => (
                  <div
                    key={execution.execution_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-slate-700 ${
                      selectedExecution?.execution_id === execution.execution_id ? "border-blue-500 bg-slate-700" : "border-slate-600"
                    }`}
                    onClick={() => setSelectedExecution(execution)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(execution.status)}
                        <div>
                          <p className="font-medium text-white">{execution.task}</p>
                          <p className="text-xs text-slate-400">
                            {new Date(execution.updated_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <Badge variant={getStatusVariant(execution.status)} className="capitalize">
                        {execution.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
                      <span>💭 {execution.thoughts.length} thoughts</span>
                      <span>⚡ {execution.actions.length} actions</span>
                      <span>📝 {execution.logs.length} logs</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Execution Details */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Execution Details</CardTitle>
            <CardDescription className="text-slate-400">
              {selectedExecution ? selectedExecution.task : "Select an execution to view details"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedExecution ? (
              <div className="text-center py-12 text-slate-400">
                <p>No execution selected</p>
                <p className="text-sm mt-2">Click on an execution from the list to view details</p>
              </div>
            ) : (
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">Status:</span>
                  <Badge variant={getStatusVariant(selectedExecution.status)} className="capitalize">
                    {selectedExecution.status}
                  </Badge>
                </div>

                {/* Final Result */}
                {selectedExecution.final_result && (
                  <div className="bg-green-900/30 border border-green-700 rounded-lg p-3">
                    <p className="text-sm font-medium text-green-400 mb-1">Final Result</p>
                    <p className="text-sm text-green-300">{selectedExecution.final_result}</p>
                  </div>
                )}

                {/* Thoughts */}
                {selectedExecution.thoughts.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      Thoughts ({selectedExecution.thoughts.length})
                    </h4>
                    <div className="space-y-2">
                      {selectedExecution.thoughts.map((thought) => (
                        <div
                          key={thought.id}
                          className="p-3 bg-slate-700/50 border border-slate-600 rounded-lg"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            {getThoughtIcon(thought.thought_type)}
                            <span className="text-xs font-medium text-slate-300 capitalize">
                              {thought.thought_type}
                            </span>
                            <span className="text-xs text-slate-500">
                              {new Date(thought.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm text-slate-300">{thought.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                {selectedExecution.actions.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                      <Play className="w-4 h-4" />
                      Actions ({selectedExecution.actions.length})
                    </h4>
                    <div className="space-y-2">
                      {selectedExecution.actions.map((action, index) => (
                        <div
                          key={action.id}
                          className={`p-3 border rounded-lg ${
                            index === selectedExecution.current_action
                              ? "border-blue-500 bg-blue-900/20"
                              : "border-slate-600 bg-slate-700/30"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getStatusIcon(action.status)}
                              {getActionIcon(action.action_type)}
                              <span className="font-medium text-sm text-white capitalize">
                                {action.action_type}
                              </span>
                            </div>
                            <Badge variant={getStatusVariant(action.status)} className="capitalize text-xs">
                              {action.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-300 mb-2">{action.description}</p>
                          {action.result && (
                            <div className="bg-green-900/20 border border-green-700/50 rounded p-2 mt-2">
                              <p className="text-xs text-green-400">Result: {action.result}</p>
                            </div>
                          )}
                          {action.error && (
                            <div className="bg-red-900/20 border border-red-700/50 rounded p-2 mt-2">
                              <p className="text-xs text-red-400">Error: {action.error}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Logs */}
                {selectedExecution.logs.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                      📝 Logs ({selectedExecution.logs.length})
                    </h4>
                    <div className="space-y-1 bg-slate-900/50 border border-slate-600 rounded-lg p-3 font-mono text-xs max-h-48 overflow-y-auto">
                      {selectedExecution.logs.map((log, index) => (
                        <div key={index} className="text-slate-300">
                          {log}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="pt-4 border-t border-slate-700">
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => deleteExecution(selectedExecution.execution_id)}
                    className="w-full"
                  >
                    Delete Execution
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
