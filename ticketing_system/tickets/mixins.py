class StaffOrCompanyFilterMixin:
    """
    Mixin providing a helper method to filter a given QuerySet
    by the current user's staff status and ticket's company.
    This assumes your objects have a `ticket` foreign key,
    and the `ticket` has `company`.
    """
    
    def filter_tickets_by_company(self, queryset):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return queryset
        else:
            return queryset.filter(company=user.company)

    def filter_by_ticket_company(self, queryset, ticket_id_field='pk'):
        """
        Filters the `queryset` so:
          - If user is staff, return all matching rows.
          - If user is not staff, restrict to rows where row.ticket.company == user.company.

        `ticket_id_field`: the name of the kwarg containing the ticket's UUID (default 'pk').
        """
        user = self.request.user
        ticket_uuid = self.kwargs[ticket_id_field]  # e.g. self.kwargs['pk']

        # Start by filtering only rows referencing this specific ticket ID
        queryset = queryset.filter(ticket__id=ticket_uuid)

        if not user.is_staff and user.role != 'admin':
            # Further filter: the ticket's company must match the user's company
            queryset = queryset.filter(ticket__company=user.company)

        return queryset
