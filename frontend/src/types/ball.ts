export interface Ball {
  id: number
  name: string
  brand: string
  weight_lbs: number
  coverstock_type: string | null
  core_type: string | null
  rg: number | null
  differential: number | null
  finish: string | null
  layout: string | null
  purpose: string | null
  hook_potential: number | null
  length_rating: number | null
  backend_rating: number | null
  is_spare_ball: boolean
  active: boolean
  notes: string | null
}
