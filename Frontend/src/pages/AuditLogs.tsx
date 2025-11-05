import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { authApi } from "@/lib/api";
import { FileText, Search, Shield } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { ExportButton } from "@/components/exports/ExportButton";

interface UserInfo {
  id: string;
  username: string;
  full_name: string;
  email: string;
}

interface AuditLog {
  id: string;
  user_info: UserInfo | null;
  action: string;
  entity_type?: string;
  entity_id?: string;
  timestamp: string;
  ip_address: string;
  status: string;
}

const AuditLogs = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      await authApi.fetchKongToken();
      const data = await authApi.getAuditLogs();
      setLogs(data);
    } catch (error: any) {
      toast({
        title: "Erreur",
        description:
          error.message || "Impossible de charger les logs d’audit.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filteredLogs = logs.filter(
    (log) =>
      (log.user_info?.username || "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.entity_type || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      success: "bg-green-500",
      error: "bg-red-500",
      warning: "bg-yellow-500",
    };
    return <Badge className={colors[status] || "bg-gray-500"}>{status}</Badge>;
  };

  if (isLoading)
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Shield className="w-8 h-8" />
          Logs d’audit
        </h1>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Rechercher par utilisateur, action..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <ExportButton
          endpoint="logs"
          data={filteredLogs}
          filename="audit-logs"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Historique d’activité
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date & Heure</TableHead>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Ressource</TableHead>
                <TableHead>Statut</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    {log.user_info
                      ? log.user_info.full_name || log.user_info.username
                      : "Système"}
                  </TableCell>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.entity_type || "-"}</TableCell>
                  <TableCell>{getStatusBadge(log.status)}</TableCell>
                </TableRow>
              ))}
              {filteredLogs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-6">
                    Aucun log trouvé.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditLogs;
