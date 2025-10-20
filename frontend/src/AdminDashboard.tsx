import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, RefreshCw, Filter } from "lucide-react";
import { fetchAdminTrials, exportTrialsCSV } from "./api";

interface TrialRecord {
  email: string;
  company: string;
  states: string[] | null;
  score: number | null;
  rating: string | null;
  started: string;
  completed: string | null;
  status: string;
}

interface TrialFilters {
  start_date?: string;
  end_date?: string;
  states?: string;
  score_min?: number;
  score_max?: number;
  status?: string;
}

function AdminDashboard() {
  const [trials, setTrials] = useState<TrialRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TrialFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [token, setToken] = useState<string>("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem("admin_token");
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadTrials();
    }
  }, [isAuthenticated]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (token) {
      localStorage.setItem("admin_token", token);
      setIsAuthenticated(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setToken("");
    setIsAuthenticated(false);
    setTrials([]);
  };

  const loadTrials = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAdminTrials(token, filters);
      setTrials(data);
    } catch (err: any) {
      setError(err.message || "Failed to load trials");
      if (err.message?.includes("401") || err.message?.includes("Unauthorized")) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      await exportTrialsCSV(token, filters);
    } catch (err: any) {
      setError(err.message || "Failed to export CSV");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = () => {
    loadTrials();
  };

  const handleClearFilters = () => {
    setFilters({});
    setTimeout(() => loadTrials(), 0);
  };

  const getRatingBadgeVariant = (rating: string | null) => {
    if (!rating) return "secondary";
    switch (rating.toLowerCase()) {
      case "healthy":
        return "default";
      case "moderate":
        return "secondary";
      case "high_risk":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "default";
      case "in_progress":
        return "secondary";
      case "started":
        return "outline";
      default:
        return "secondary";
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("en-AU", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle>Admin Login</CardTitle>
            <CardDescription>Enter your authentication token to access the admin dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="token">Authentication Token</Label>
                <Input
                  id="token"
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Enter your JWT token"
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
            <p className="text-muted-foreground">Manage compliance assessment trials</p>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Trials List</CardTitle>
                <CardDescription>View and filter all assessment trials</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter className="w-4 h-4 mr-2" />
                  {showFilters ? "Hide" : "Show"} Filters
                </Button>
                <Button variant="outline" size="sm" onClick={loadTrials} disabled={loading}>
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                  Refresh
                </Button>
                <Button size="sm" onClick={handleExport} disabled={loading}>
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {showFilters && (
              <div className="mb-6 p-4 border rounded-lg bg-accent/50">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="space-y-2">
                    <Label htmlFor="start_date">Start Date</Label>
                    <Input
                      id="start_date"
                      type="date"
                      value={filters.start_date || ""}
                      onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="end_date">End Date</Label>
                    <Input
                      id="end_date"
                      type="date"
                      value={filters.end_date || ""}
                      onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select
                      value={filters.status || "all"}
                      onValueChange={(value) => setFilters({ ...filters, status: value === "all" ? undefined : value })}
                    >
                      <SelectTrigger id="status">
                        <SelectValue placeholder="All statuses" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All statuses</SelectItem>
                        <SelectItem value="started">Started</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="score_min">Min Score</Label>
                    <Input
                      id="score_min"
                      type="number"
                      min="0"
                      max="100"
                      value={filters.score_min || ""}
                      onChange={(e) =>
                        setFilters({ ...filters, score_min: e.target.value ? Number(e.target.value) : undefined })
                      }
                      placeholder="0"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="score_max">Max Score</Label>
                    <Input
                      id="score_max"
                      type="number"
                      min="0"
                      max="100"
                      value={filters.score_max || ""}
                      onChange={(e) =>
                        setFilters({ ...filters, score_max: e.target.value ? Number(e.target.value) : undefined })
                      }
                      placeholder="100"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="states">States (comma-separated)</Label>
                    <Input
                      id="states"
                      value={filters.states || ""}
                      onChange={(e) => setFilters({ ...filters, states: e.target.value })}
                      placeholder="NSW,VIC,QLD"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleApplyFilters} disabled={loading}>
                    Apply Filters
                  </Button>
                  <Button variant="outline" onClick={handleClearFilters} disabled={loading}>
                    Clear Filters
                  </Button>
                </div>
              </div>
            )}

            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>States</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Rating</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && trials.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">
                        Loading...
                      </TableCell>
                    </TableRow>
                  ) : trials.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                        No trials found
                      </TableCell>
                    </TableRow>
                  ) : (
                    trials.map((trial, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{trial.email}</TableCell>
                        <TableCell>{trial.company}</TableCell>
                        <TableCell>{trial.states ? trial.states.join(", ") : "-"}</TableCell>
                        <TableCell>{trial.score !== null ? trial.score.toFixed(1) : "-"}</TableCell>
                        <TableCell>
                          {trial.rating ? (
                            <Badge variant={getRatingBadgeVariant(trial.rating)}>
                              {trial.rating.replace("_", " ")}
                            </Badge>
                          ) : (
                            "-"
                          )}
                        </TableCell>
                        <TableCell>{formatDate(trial.started)}</TableCell>
                        <TableCell>{formatDate(trial.completed)}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusBadgeVariant(trial.status)}>
                            {trial.status.replace("_", " ")}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>

            <div className="mt-4 text-sm text-muted-foreground">
              Showing {trials.length} trial{trials.length !== 1 ? "s" : ""}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AdminDashboard;
