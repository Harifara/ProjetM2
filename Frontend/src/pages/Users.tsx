import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { authApi } from "@/lib/api";
import { UserPlus, Search, Edit, Trash2, Eye, Users as UsersIcon } from "lucide-react";
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

// =====================
// 🔹 Utilitaire UUID
// =====================
const cleanUUID = (id: string) => id.replace(/\s/g, "").trim();

const validRoles = [
  "admin",
  "responsable_rh",
  "responsable_stock",
  "responsable_finance",
  "magasinier",
  "coordinateur",
];

const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
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

  // =====================
  // 🔹 Récupération des utilisateurs
  // =====================
  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      await authApi.fetchKongToken();
      const data = await authApi.getUsers();
      setUsers(data);
    } catch (error: any) {
      toast({
        title: "Erreur",
        description: error.message || "Impossible de charger les utilisateurs.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // =====================
  // 🔹 Ouverture/Fermeture modal formulaire
  // =====================
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

  // =====================
  // 🔹 Ouverture/Fermeture modal détails
  // =====================
  const handleOpenDetail = (user: User) => {
    setSelectedUser(user);
    setIsDetailOpen(true);
  };

  const handleCloseDetail = () => {
    setIsDetailOpen(false);
    setSelectedUser(null);
  };

  // =====================
  // 🔹 Création / Mise à jour
  // =====================
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Vérification mot de passe pour création
    if (!selectedUser && (!formData.password || formData.password !== formData.password_confirm)) {
      toast({
        title: "Erreur",
        description: "Les mots de passe ne correspondent pas ou sont vides.",
        variant: "destructive",
      });
      return;
    }

    // Vérification rôle valide
    if (!validRoles.includes(formData.role)) {
      toast({
        title: "Erreur",
        description: "Le rôle sélectionné n'est pas valide.",
        variant: "destructive",
      });
      return;
    }

    try {
      await authApi.fetchKongToken();

      if (selectedUser) {
        // Mise à jour utilisateur existant
        const updateData: any = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          is_active: formData.is_active,
        };

        if (formData.password && formData.password.trim() !== "") {
          updateData.password = formData.password_confirm && formData.password_confirm.trim() !== ""
            ? formData.password_confirm
            : formData.password;
        }

        await authApi.updateUser(cleanUUID(selectedUser.id), updateData);
        toast({ title: "Succès", description: "Utilisateur mis à jour." });
      } else {
        // Création utilisateur
        if (!formData.password || formData.password.trim() === "" || formData.password !== formData.password_confirm) {
          toast({
            title: "Erreur",
            description: "Les mots de passe ne correspondent pas ou sont vides.",
            variant: "destructive",
          });
          return;
        }

        await authApi.register({
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
          password_confirm: formData.password_confirm,
          role: formData.role,
          is_active: formData.is_active,
        });

        toast({ title: "Succès", description: "Utilisateur créé." });
      }

      await fetchUsers();
      handleCloseModal();
    } catch (error: any) {
      toast({
        title: "Erreur",
        description: error.message || "Erreur lors de l'opération.",
        variant: "destructive",
      });
    }
  };

  // =====================
  // 🔹 Suppression utilisateur
  // =====================
  const handleDelete = async (id: string) => {
    if (!confirm("Supprimer cet utilisateur ?")) return;
    try {
      await authApi.fetchKongToken();
      await authApi.deleteUser(cleanUUID(id));
      toast({ title: "Succès", description: "Utilisateur supprimé." });
      await fetchUsers();
    } catch (error: any) {
      toast({
        title: "Erreur",
        description: error.message || "Erreur lors de la suppression.",
        variant: "destructive",
      });
    }
  };

  // =====================
  // 🔹 Filtrage utilisateurs
  // =====================
  const filteredUsers = users.filter(
    (u) =>
      u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadge = (role: string) => {
    const colors: Record<string, string> = {
      admin: "bg-red-500",
      responsable_rh: "bg-blue-500",
      responsable_stock: "bg-green-500",
      responsable_finance: "bg-purple-500",
      magasinier: "bg-orange-500",
      coordinateur: "bg-cyan-500",
    };
    return <Badge className={colors[role] || "bg-gray-500"}>{role}</Badge>;
  };

  if (isLoading)
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <UsersIcon className="w-8 h-8" /> Gestion des utilisateurs
        </h1>
        <Button onClick={() => handleOpenModal()} className="gap-2">
          <UserPlus className="w-4 h-4" /> Ajouter un utilisateur
        </Button>
      </div>

      {/* Recherche + Export */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Rechercher par nom, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <ExportButton endpoint="users" data={filteredUsers} filename="utilisateurs" />
      </div>

      {/* Liste utilisateurs */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des utilisateurs</CardTitle>
        </CardHeader>
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
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{getRoleBadge(user.role)}</TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "default" : "destructive"}>
                      {user.is_active ? "Actif" : "Inactif"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button size="sm" variant="outline" onClick={() => handleOpenDetail(user)}>
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(user)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => handleDelete(user.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filteredUsers.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-6">
                    Aucun utilisateur trouvé.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Modal Détails */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Détails de l'utilisateur</DialogTitle>
            <DialogDescription>Informations complètes de l'utilisateur sélectionné.</DialogDescription>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-3">
              <p><strong>Nom d’utilisateur :</strong> {selectedUser.username}</p>
              <p><strong>Nom complet :</strong> {selectedUser.full_name}</p>
              <p><strong>Email :</strong> {selectedUser.email}</p>
              <p><strong>Rôle :</strong> {selectedUser.role}</p>
              <p><strong>Statut :</strong> {selectedUser.is_active ? "Actif" : "Inactif"}</p>
            </div>
          )}
          <DialogFooter>
            <Button onClick={handleCloseDetail}>Fermer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Formulaire */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{selectedUser ? "Modifier l'utilisateur" : "Créer un utilisateur"}</DialogTitle>
            <DialogDescription>
              {selectedUser ? "Modifiez les informations ci-dessous." : "Entrez les informations du nouvel utilisateur."}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Nom d’utilisateur</Label>
              <Input
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="full_name">Nom complet</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="password">Mot de passe</Label>
              <Input
                id="password"
                type="password"
                placeholder={selectedUser ? "Laisser vide pour ne pas changer" : ""}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="password_confirm">Confirmer le mot de passe</Label>
              <Input
                id="password_confirm"
                type="password"
                placeholder={selectedUser ? "Laisser vide pour ne pas changer" : ""}
                value={formData.password_confirm}
                onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
              />
            </div>

            <div>
              <Label>Rôle</Label>
              <Select value={formData.role} onValueChange={(v) => setFormData({ ...formData, role: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un rôle" />
                </SelectTrigger>
                <SelectContent>
                  {validRoles.map((r) => (
                    <SelectItem key={r} value={r}>
                      {r.replace("_", " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <input
                id="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              <Label htmlFor="is_active">Compte actif</Label>
            </div>

            <DialogFooter>
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
