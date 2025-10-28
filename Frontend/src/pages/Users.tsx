// src/pages/Users.tsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { authApi } from "@/lib/api";
import { UserPlus, Search, Edit, Trash2, Users as UsersIcon } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { ExportButton } from "@/components/exports/ExportButton";

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface FormData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  password_confirm?: string;
  role: string;
  is_active: boolean;
}

const validRoles = ["admin", "responsable_rh", "responsable_stock", "responsable_finance", "magasinier", "coordinateur"];

const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<FormData>({
    username: "",
    email: "",
    full_name: "",
    password: "",
    password_confirm: "",
    role: "magasinier",
    is_active: true,
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const data = await authApi.getUsers();
      setUsers(data);
    } catch (error: any) {
      toast({ title: "Erreur", description: error.message || "Impossible de charger les utilisateurs", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = (user?: User) => {
    if (user) {
      setSelectedUser(user);
      setFormData({
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        password: "",
        password_confirm: "",
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      setSelectedUser(null);
      setFormData({
        username: "",
        email: "",
        full_name: "",
        password: "",
        password_confirm: "",
        role: "magasinier",
        is_active: true,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Vérification des mots de passe si création ou modification
    if (!selectedUser || formData.password || formData.password_confirm) {
      if (formData.password !== formData.password_confirm) {
        toast({ title: "Erreur", description: "Les mots de passe ne correspondent pas.", variant: "destructive" });
        return;
      }
    }

    // Vérifier que le rôle est valide
    if (!validRoles.includes(formData.role)) {
      toast({ title: "Erreur", description: "Le rôle sélectionné n'est pas valide.", variant: "destructive" });
      return;
    }

    try {
      if (selectedUser) {
        // Mise à jour
        const updateData: any = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          is_active: formData.is_active,
        };
        if (formData.password) {
          updateData.password = formData.password;
          updateData.password_confirm = formData.password_confirm || formData.password;
        }
        await authApi.updateUser(selectedUser.id, updateData);
        toast({ title: "Succès", description: "Utilisateur mis à jour." });
      } else {
        // Création
        await authApi.register({
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
          password_confirm: formData.password_confirm || formData.password,
          role: formData.role,
          is_active: formData.is_active,
        });
        toast({ title: "Succès", description: "Utilisateur créé." });
      }

      await fetchUsers();
      handleCloseModal();
    } catch (error: any) {
      toast({ title: "Erreur", description: error.message || "Erreur lors de l'opération.", variant: "destructive" });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ?")) return;
    try {
      await authApi.deleteUser(id);
      toast({ title: "Succès", description: "Utilisateur supprimé." });
      await fetchUsers();
    } catch (error: any) {
      toast({ title: "Erreur", description: error.message || "Erreur lors de la suppression de l’utilisateur.", variant: "destructive" });
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadge = (role: string) => {
    const roleColors: Record<string, string> = {
      admin: "bg-red-500",
      responsable_rh: "bg-blue-500",
      responsable_stock: "bg-green-500",
      responsable_finance: "bg-purple-500",
      magasinier: "bg-orange-500",
      coordinateur: "bg-cyan-500",
    };
    return <Badge className={roleColors[role] || "bg-gray-500"}>{role}</Badge>;
  };

  if (isLoading) return <div className="p-8 space-y-6"><Skeleton className="h-12 w-full"/><Skeleton className="h-64 w-full"/></div>;

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <UsersIcon className="w-8 h-8" /> Gestion des utilisateurs
          </h1>
          <p className="text-muted-foreground mt-2">Gérer les comptes utilisateurs et leurs accès</p>
        </div>
        <Button onClick={() => handleOpenModal()} className="gap-2">
          <UserPlus className="w-4 h-4" /> Ajouter un utilisateur
        </Button>
      </div>

      {/* Search & Export */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input placeholder="Rechercher par nom, email..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
        </div>
        <ExportButton endpoint="users" data={filteredUsers} filename="utilisateurs" />
      </div>

      {/* Statistiques par rôle */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        {validRoles.map((role) => {
          const count = users.filter((u) => u.role === role).length;
          const roleNames: Record<string, string> = {
            admin: "Admins",
            responsable_rh: "RH",
            responsable_stock: "Stock",
            responsable_finance: "Finance",
            magasinier: "Magasiniers",
            coordinateur: "Coordinateurs",
          };
          const roleIcons: Record<string, JSX.Element> = {
            admin: <UsersIcon className="w-8 h-8 text-red-500" />,
            responsable_rh: <UsersIcon className="w-8 h-8 text-blue-500" />,
            responsable_stock: <UsersIcon className="w-8 h-8 text-green-500" />,
            responsable_finance: <UsersIcon className="w-8 h-8 text-purple-500" />,
            magasinier: <UsersIcon className="w-8 h-8 text-orange-500" />,
            coordinateur: <UsersIcon className="w-8 h-8 text-cyan-500" />,
          };
          return (
            <Card key={role}>
              <CardContent className="p-6 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{roleNames[role]}</p>
                  <p className="text-2xl font-bold text-foreground">{count}</p>
                </div>
                {roleIcons[role]}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Liste des utilisateurs */}
      <Card>
        <CardHeader><CardTitle>Liste des utilisateurs</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nom d'utilisateur</TableHead>
                <TableHead>Nom complet</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Rôle</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.username}</TableCell>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{getRoleBadge(user.role)}</TableCell>
                  <TableCell><Badge variant={user.is_active ? "default" : "destructive"}>{user.is_active ? "Actif" : "Inactif"}</Badge></TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleOpenModal(user)}><Edit className="w-4 h-4"/></Button>
                      <Button variant="destructive" size="sm" onClick={() => handleDelete(user.id)}><Trash2 className="w-4 h-4"/></Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{selectedUser ? "Modifier l'utilisateur" : "Nouvel utilisateur"}</DialogTitle>
            <DialogDescription>{selectedUser ? "Modifier les informations de l'utilisateur" : "Créer un nouveau compte utilisateur"}</DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Nom d'utilisateur</Label>
              <Input id="username" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} required />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
            </div>

            <div>
              <Label htmlFor="full_name">Nom complet</Label>
              <Input id="full_name" value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} required />
            </div>

            <div>
              <Label htmlFor="password">Mot de passe</Label>
              <Input id="password" type="password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} placeholder={selectedUser ? "Laisser vide pour ne pas changer" : ""} />
            </div>

            <div>
              <Label htmlFor="password_confirm">Confirmer le mot de passe</Label>
              <Input id="password_confirm" type="password" value={formData.password_confirm} onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })} placeholder={selectedUser ? "Laisser vide pour ne pas changer" : ""} />
            </div>

            <div>
              <Label htmlFor="role">Rôle</Label>
              <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un rôle" />
                </SelectTrigger>
                <SelectContent>
                  {validRoles.map((role) => (
                    <SelectItem key={role} value={role}>{role.charAt(0).toUpperCase() + role.slice(1).replace("_", " ")}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <input id="is_active" type="checkbox" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />
              <Label htmlFor="is_active">Compte actif</Label>
            </div>

            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={handleCloseModal}>Annuler</Button>
              <Button type="submit">{selectedUser ? "Mettre à jour" : "Créer"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Users;
