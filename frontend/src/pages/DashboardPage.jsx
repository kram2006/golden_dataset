import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Play, RefreshCw, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const { toast } = useToast();
  const [hasApiKey, setHasApiKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [models, setModels] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [maxIterations, setMaxIterations] = useState(20);
  const [runs, setRuns] = useState([]);
  const [currentRun, setCurrentRun] = useState(null);
  const [logs, setLogs] = useState([]);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    let interval;
    if (currentRun && currentRun.status === 'running') {
      interval = setInterval(() => {
        refreshRunStatus();
        refreshLogs();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [currentRun]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [configRes, modelsRes, tasksRes, runsRes] = await Promise.all([
        axios.get(`${API}/automation/config`),
        axios.get(`${API}/automation/models`),
        axios.get(`${API}/automation/tasks`),
        axios.get(`${API}/automation/runs`)
      ]);

      setHasApiKey(configRes.data.has_api_key);
      setModels(modelsRes.data.models || []);
      setTasks(tasksRes.data.tasks || []);
      setRuns(runsRes.data.runs || []);

      // Select first model by default
      if (modelsRes.data.models && modelsRes.data.models.length > 0) {
        setSelectedModels([modelsRes.data.models[0].id]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboard data',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshRunStatus = async () => {
    if (!currentRun) return;
    try {
      const response = await axios.get(`${API}/automation/runs/${currentRun.run_id}`);
      setCurrentRun(response.data);
      
      // If run completed, refresh runs list
      if (response.data.status !== 'running') {
        const runsRes = await axios.get(`${API}/automation/runs`);
        setRuns(runsRes.data.runs || []);
      }
    } catch (error) {
      console.error('Error refreshing run status:', error);
    }
  };

  const refreshLogs = async () => {
    try {
      const response = await axios.get(`${API}/automation/logs?lines=100`);
      setLogs(response.data.logs || []);
    } catch (error) {
      console.error('Error refreshing logs:', error);
    }
  };

  const handleStart = async () => {
    if (selectedModels.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one model',
        variant: 'destructive'
      });
      return;
    }

    try {
      setStarting(true);
      const response = await axios.post(`${API}/automation/start`, {
        models: selectedModels,
        tasks: selectedTasks.length > 0 ? selectedTasks : null,
        max_iterations: maxIterations
      });

      toast({
        title: 'Success',
        description: 'Automation started successfully',
      });

      // Get the run details
      const runRes = await axios.get(`${API}/automation/runs/${response.data.run_id}`);
      setCurrentRun(runRes.data);
      refreshLogs();
    } catch (error) {
      console.error('Error starting automation:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to start automation',
        variant: 'destructive'
      });
    } finally {
      setStarting(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'secondary',
      running: 'default',
      completed: 'success',
      failed: 'destructive',
      cancelled: 'outline'
    };
    return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!hasApiKey) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Alert className="bg-yellow-50 border-yellow-200">
          <AlertCircle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            Please configure your OpenRouter API key in the Configuration page before running automation.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Automation Dashboard</h1>
        <p className="text-gray-600">Configure and run LLM testing automation</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>Select models and tasks to run</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Model Selection */}
              <div className="space-y-2">
                <Label>Models ({selectedModels.length} selected)</Label>
                <ScrollArea className="h-48 border rounded-md p-4">
                  {models.map((model) => (
                    <div key={model.id} className="flex items-start space-x-2 mb-3">
                      <Checkbox
                        id={model.id}
                        checked={selectedModels.includes(model.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedModels([...selectedModels, model.id]);
                          } else {
                            setSelectedModels(selectedModels.filter(m => m !== model.id));
                          }
                        }}
                      />
                      <div className="grid gap-1.5 leading-none">
                        <label
                          htmlFor={model.id}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                        >
                          {model.name}
                        </label>
                        {model.description && (
                          <p className="text-xs text-gray-500">{model.description.substring(0, 50)}...</p>
                        )}
                      </div>
                    </div>
                  ))}
                </ScrollArea>
              </div>

              {/* Task Selection */}
              <div className="space-y-2">
                <Label>Tasks ({selectedTasks.length > 0 ? selectedTasks.length : 'All'} selected)</Label>
                <ScrollArea className="h-32 border rounded-md p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Checkbox
                      id="all-tasks"
                      checked={selectedTasks.length === 0}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedTasks([]);
                        }
                      }}
                    />
                    <Label htmlFor="all-tasks" className="cursor-pointer font-semibold">
                      All Tasks
                    </Label>
                  </div>
                  {tasks.map((task) => (
                    <div key={task} className="flex items-center space-x-2 mb-2">
                      <Checkbox
                        id={task}
                        checked={selectedTasks.includes(task)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedTasks([...selectedTasks, task]);
                          } else {
                            setSelectedTasks(selectedTasks.filter(t => t !== task));
                          }
                        }}
                      />
                      <Label htmlFor={task} className="cursor-pointer">{task}</Label>
                    </div>
                  ))}
                </ScrollArea>
              </div>

              {/* Max Iterations */}
              <div className="space-y-2">
                <Label htmlFor="iterations">Max Iterations</Label>
                <Input
                  id="iterations"
                  type="number"
                  min="1"
                  max="50"
                  value={maxIterations}
                  onChange={(e) => setMaxIterations(parseInt(e.target.value) || 20)}
                />
              </div>

              {/* Start Button */}
              <Button
                className="w-full"
                onClick={handleStart}
                disabled={starting || (currentRun && currentRun.status === 'running')}
              >
                {starting ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Starting...</>
                ) : currentRun && currentRun.status === 'running' ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Running...</>
                ) : (
                  <><Play className="mr-2 h-4 w-4" /> Start Automation</>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Current Run Status */}
          {currentRun && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Current Run</span>
                  {getStatusBadge(currentRun.status)}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Run ID:</span>
                  <span className="font-mono text-xs">{currentRun.run_id.substring(0, 8)}...</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Tasks:</span>
                  <span>{currentRun.total_tasks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Completed:</span>
                  <span className="text-green-600">{currentRun.completed_tasks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Failed:</span>
                  <span className="text-red-600">{currentRun.failed_tasks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Started:</span>
                  <span>{new Date(currentRun.start_time).toLocaleString()}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-2"
                  onClick={refreshRunStatus}
                >
                  <RefreshCw className="mr-2 h-3 w-3" /> Refresh
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Monitoring Panel */}
        <div className="lg:col-span-2">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle>Monitoring</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <Tabs defaultValue="logs" className="h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="logs">Live Logs</TabsTrigger>
                  <TabsTrigger value="history">Run History</TabsTrigger>
                </TabsList>
                <TabsContent value="logs" className="flex-1 overflow-hidden">
                  <ScrollArea className="h-full border rounded-md p-4 bg-gray-950">
                    <div className="font-mono text-xs text-green-400 space-y-1">
                      {logs.length === 0 ? (
                        <div className="text-gray-500">No logs yet. Start an automation to see logs here.</div>
                      ) : (
                        logs.map((log, i) => (
                          <div key={i}>{log}</div>
                        ))
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>
                <TabsContent value="history" className="flex-1 overflow-hidden">
                  <ScrollArea className="h-full">
                    <div className="space-y-2">
                      {runs.length === 0 ? (
                        <div className="text-gray-500 text-center py-8">No runs yet</div>
                      ) : (
                        runs.slice().reverse().map((run) => (
                          <Card key={run.run_id} className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-mono text-xs text-gray-500">
                                    {run.run_id.substring(0, 8)}
                                  </span>
                                  {getStatusBadge(run.status)}
                                </div>
                                <div className="text-sm text-gray-600">
                                  {run.models.length} models × {run.tasks.length} tasks
                                </div>
                                <div className="text-xs text-gray-500">
                                  {new Date(run.start_time).toLocaleString()}
                                </div>
                              </div>
                              <div className="text-right text-sm">
                                <div className="text-green-600">{run.completed_tasks} ✓</div>
                                <div className="text-red-600">{run.failed_tasks} ✗</div>
                              </div>
                            </div>
                          </Card>
                        ))
                      )}
                    </div>
                  </ScrollArea>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
