import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Loader2, XCircle, Play, RefreshCw } from "lucide-react";

interface ProgressStep {
  id: string;
  name: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  progress: number;
  message?: string;
  started_at?: string;
  completed_at?: string;
}

interface TaskProgress {
  task_id: string;
  name: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  steps: ProgressStep[];
  current_step: number;
  overall_progress: number;
  created_at: string;
  updated_at: string;
  error?: string;
}

interface ProgressDisplayProps {
  apiBaseUrl?: string;
}

export default function ProgressDisplay({ apiBaseUrl = "http://localhost:7777" }: ProgressDisplayProps) {
  const [tasks, setTasks] = useState<TaskProgress[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch all tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/progress/tasks`);
      const data = await response.json();
      setTasks(data.tasks || []);

      // Update selected task if exists
      if (selectedTask) {
        const updated = data.tasks.find((t: TaskProgress) => t.task_id === selectedTask.task_id);
        if (updated) {
          setSelectedTask(updated);
        }
      }
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    }
  };

  // Start demo task
  const startDemoTask = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/progress/demo`, {
        method: "POST",
      });
      const data = await response.json();

      // Wait a moment then fetch tasks to get the new task
      setTimeout(() => {
        fetchTasks();
      }, 500);
    } catch (error) {
      console.error("Failed to start demo task:", error);
    } finally {
      setLoading(false);
    }
  };

  // Delete task
  const deleteTask = async (taskId: string) => {
    try {
      await fetch(`${apiBaseUrl}/progress/task/${taskId}`, {
        method: "DELETE",
      });
      fetchTasks();
      if (selectedTask?.task_id === taskId) {
        setSelectedTask(null);
      }
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  // Auto-refresh when a task is in progress
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      const hasInProgress = tasks.some((t) => t.status === "in_progress");
      if (hasInProgress || selectedTask?.status === "in_progress") {
        fetchTasks();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, tasks, selectedTask]);

  // Initial fetch
  useEffect(() => {
    fetchTasks();
  }, []);

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "in_progress":
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
      case "in_progress":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Progress Tracking</h2>
          <p className="text-sm text-muted-foreground">Monitor task execution in real-time</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? "animate-spin" : ""}`} />
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
          </Button>
          <Button onClick={startDemoTask} disabled={loading}>
            <Play className="w-4 h-4 mr-2" />
            {loading ? "Starting..." : "Start Demo Task"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task List */}
        <Card>
          <CardHeader>
            <CardTitle>All Tasks</CardTitle>
            <CardDescription>
              {tasks.length} task{tasks.length !== 1 ? "s" : ""} tracked
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {tasks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No tasks yet</p>
                  <p className="text-sm mt-2">Click "Start Demo Task" to see progress tracking</p>
                </div>
              ) : (
                tasks.map((task) => (
                  <div
                    key={task.task_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-accent ${
                      selectedTask?.task_id === task.task_id ? "border-primary bg-accent" : ""
                    }`}
                    onClick={() => setSelectedTask(task)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        <div>
                          <p className="font-medium">{task.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(task.updated_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <Badge variant={getStatusVariant(task.status)}>
                        {task.status}
                      </Badge>
                    </div>
                    <Progress value={task.overall_progress} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-1">
                      {task.overall_progress.toFixed(1)}% complete
                    </p>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Task Details */}
        <Card>
          <CardHeader>
            <CardTitle>Task Details</CardTitle>
            <CardDescription>
              {selectedTask ? selectedTask.name : "Select a task to view details"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedTask ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>No task selected</p>
                <p className="text-sm mt-2">Click on a task from the list to view details</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Overall Progress */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Overall Progress</span>
                    <span className="text-sm text-muted-foreground">
                      {selectedTask.overall_progress.toFixed(1)}%
                    </span>
                  </div>
                  <Progress value={selectedTask.overall_progress} className="h-3" />
                </div>

                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge variant={getStatusVariant(selectedTask.status)} className="capitalize">
                    {selectedTask.status.replace("_", " ")}
                  </Badge>
                </div>

                {/* Steps */}
                <div>
                  <h4 className="text-sm font-medium mb-3">Steps</h4>
                  <div className="space-y-3">
                    {selectedTask.steps.map((step, index) => (
                      <div
                        key={step.id}
                        className={`p-3 border rounded-lg ${
                          index === selectedTask.current_step ? "border-primary bg-accent" : ""
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(step.status)}
                            <span className="font-medium text-sm">{step.name}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {step.progress.toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={step.progress} className="h-1.5" />
                        {step.message && (
                          <p className="text-xs text-muted-foreground mt-2">{step.message}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-4 border-t">
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => deleteTask(selectedTask.task_id)}
                    className="w-full"
                  >
                    Delete Task
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
